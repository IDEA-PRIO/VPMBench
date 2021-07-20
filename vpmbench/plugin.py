import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Union, List

import docker
from docker.types import Mount
from pandas import DataFrame, Series
from pandera import DataFrameSchema, Column, Float, Check, Int

from vpmbench import log
from vpmbench.enums import ReferenceGenome, VariationType
from vpmbench.processors import format_input, format_output


class EntryPoint(ABC):
    """ Represent an entry point to the custom processing logic required to invoke a prioritization method.
    """

    @abstractmethod
    def run(self, variant_information_table: DataFrame) -> DataFrame:
        """ Run the custom processing logic

        Has to return a :class:`~panda.DataFrame` with two columns:

            * UID: The UID of the variants
            * SCORE: The calculated score for the variants

        Parameters
        ----------
        variant_information_table
            The variant information table

        Returns
        -------
        DataFrame
            The results from the processing logic
        """
        pass


@dataclass
class DockerEntryPoint(EntryPoint):
    """ Represent an entry point using Docker to run the custom processing logic

    Parameters
    ---------
    image
        The name of the Docker image used to create a Docker container
    run_command
        The command that invokes the custom processing logic in the Docker container input Information about the ``file-path`` and ``format`` of the input file.
    output
        Information about the ``file-path`` and ``format`` of the output file.
    bindings
        Additional bindings that should be mounted for Docker container. Keys: local file paths, Values: remote file paths
    """
    image: str
    run_command: str
    input: dict
    output: dict
    bindings: dict = None

    @staticmethod
    def _create_files():
        return tempfile.NamedTemporaryFile("w+t"), tempfile.NamedTemporaryFile("w+t", delete=False)

    def _mount_everything(self, in_file, out_file):
        in_file_mount = Mount(self.input["file-path"], in_file.name, type="bind")
        out_file_mount = Mount(self.output["file-path"], out_file.name, type="bind")
        bind_mounts = []
        for local_path, remote_path in self.bindings.items():
            mount = Mount(remote_path, local_path, type="bind")
            bind_mounts.append(mount)
        return bind_mounts + [in_file_mount, out_file_mount]

    def run(self, variant_information_table: DataFrame) -> DataFrame:
        """ Run the custom processing for the entry point.

        The `variant_information_table` is converted into the expected input file format using
        :func:`~vpmbench.processors.format_input`. The results from the Docker container are converted using
        :func:`~vpmbench.processors.format_output`.

        Parameters
        ----------
        variant_information_table
            The variant information table

        Returns
        -------
        DataFrame
            The results from the processing logic

        """
        in_file, out_file = self._create_files()
        format_input(variant_information_table, self.input["format"], in_file.name, **self.input.get("args", {}))
        mounts = self._mount_everything(in_file, out_file)
        client = docker.from_env()
        client.ping()
        client.containers.run(self.image, self.run_command, mounts=mounts, privileged=True)
        return format_output(variant_information_table, self.output["format"], out_file.name,
                             **self.output.get("args", {}))


@dataclass
class PythonEntryPoint(EntryPoint):
    """ Represent an entry point using Python to run the custom processing logic

    The entry point has to be implemented in the Python file via a function ``entry_point`` accepting the
    :meth:`~vpmbench.data.EvaluationData.variant_data` as input.

    Parameters
    ----------
    file_path
        Path the Python file containing the implementation of the custom processing logic
    plugin
        Reference to the plugin of the entry point
    """
    file_path: Path

    def run(self, variant_information_table: Path) -> DataFrame:
        spec = spec_from_file_location(__name__, self.file_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.entry_point(variant_information_table)


@dataclass
class Plugin:
    """ Represent a plugin

    Basically, the plugin stores the information from the manifest files.

    Parameters
    -----------
    name
        The name of the plugin

    version
        The version of the plugin

    supported_variations
        The variation types supported by the prioritization method

    reference_genome
        The reference genome supported by the prioritization method

    databases
        The accompanying databased of the prioritization method; Key: name of the database, Value: version of
        the database

    entry_point
        The entry point

    cutoff
        The cutoff for pathogenicity

    manifest_path
        The file path to the manifest file for the plugin
    """
    name: str
    version: str
    supported_variations: List[VariationType]
    supported_chromosomes: List[str]
    supported_reference_allels = []
    supported_alternative_allels = []
    reference_genome: ReferenceGenome
    databases: List[str]
    entry_point: EntryPoint
    cutoff: float
    manifest_path: Union[str, Path]

    @property
    def score_column_name(self) -> str:
        """ Return the column name for the :class:`~vpmbench.data.AnnotatedVariantData`.

        The name is calculated by ``\"{self.name}_SCORE"``.

        Returns
        -------
        str
            The name of the column
        """
        return f"{self.name}_SCORE"

    def run(self, variant_information_table: DataFrame) -> DataFrame:
        """ Run the plugin on the `variant_information_table`

        Before running the plugin the :meth:`compatibility <vpmbench.plugin.Plugin.is_compatible_with_data>` of the
        data with the plugin is tested. Next the :meth:`~vpmbench.plugin.EntryPoint.run` method of the entry_point is
        called with the `variant_information_table`. The result of the entry_point is :meth:`validated
        <vpmbench.plugin.Plugin._validate_score_table>` to ensure that each variant from the
        variant_information_table got a valid score assigned. Finally, the score column is renamed using the
        :meth:`~vpmbench.plugin.Plugin.score_column_name`.

        The resulting Dataframe consists of two columns:

            * UID: The UID of the variants
            *  :meth:`~vpmbench.plugin.Plugin.score_column_name`: The scores from the prioritization method

        Parameters
        ----------
        variant_information_table
            The variant information table

        Returns
        -------
        DataFrame
            The plugin result.

        """
        self.is_compatible_with_data(variant_information_table)
        log.debug(f"Invoke method: {self.name}")
        score_table = self.entry_point.run(variant_information_table)
        log.debug(f"Finish method: {self.name}")
        self._validate_score_table(variant_information_table, score_table)
        return score_table.rename(columns={"SCORE": self.score_column_name})

    @staticmethod
    def _validate_score_table(variant_information_table: DataFrame, score_table: DataFrame):
        """ Validate the results of the prioritization method.

        The following constraints are checked:

            * Each UID from the variant_information_table is also in the score_table
            * Each SCORE in the score_table is a numerical value

        Parameters
        ----------
        variant_information_table :
            The variant information table

        score_table :
            The scoring results from the prioritization method

        Raises
        ------
        :class:`~pandera.errors.SchemaErrors`
            If the validation of the data fails
        """
        variants_uid = variant_information_table["UID"]
        schema = DataFrameSchema({
            "UID": Column(Int, Check(lambda x: variants_uid.isin(x) & x.isin(variants_uid)), required=True),
            "SCORE": Column(Float, coerce=True, required=True)})
        schema.validate(score_table, lazy=True)

    def __hash__(self) -> int:
        return self.name.__hash__()

    def is_compatible_with_data(self, variant_information_table: Union['EvaluationData', DataFrame]):
        """ Check if the plugin is compatible with the variant information table.

        The following constraints are checked:

            * In the variant information table are only variants with the same reference genome as the plugin
            * In the variant table are only variants with a variation type supported by the plugin

        Parameters
        ----------
        variant_information_table :
            The variant information table

        Raises
        -------
        RuntimeError
            If the validation fails
        """
        from vpmbench.data import EvaluationData
        if isinstance(variant_information_table, EvaluationData):
            return self.is_compatible_with_data(variant_information_table.variant_data)

        variant_rgs = variant_information_table["RG"].unique()
        if not all([rg == self.reference_genome for rg in variant_rgs]):
            raise RuntimeError(
                f"Plugin '{self.name}' is not compatible with data: Reference genome of method not compatible data!")

        variant_types = set(variant_information_table["TYPE"].unique())
        supported_variation_types = set(self.supported_variations)
        if not variant_types.issubset(supported_variation_types):
            raise RuntimeError(
                f"Plugin '{self.name}' is not compatible with data: Supported variation type of method not compatible data! "
                f"Method does not support the following variantion types found in data: {variant_types - supported_variation_types}")

        variant_chroms = set(variant_information_table["CHROM"].unique())
        supported_chroms = set(self.supported_chromosomes)
        if not variant_chroms.issubset(supported_chroms):
            raise RuntimeError(
                f"Plugin '{self.name}' is not compatible with data: Data contains unsupported chromosomes! "
                f"Method does not support the following chromosomes found in data: {variant_chroms - supported_chroms}")


class PluginBuilder:
    """ This class builds the :class:`Plugins <vpmbench.plugin.Plugin>`

    """

    @classmethod
    def build_plugin(cls, **kwargs) -> Plugin:
        """ Build a plugin from the arguments.

        See the documentation for specification the manifest schema.

        Parameters
        ----------
        kwargs :
            The arguments

        Returns
        -------
        Plugin
            The Plugin

        Raises
        ------
        RuntimeError
            If required in formation is missing.

        """
        cls.validate_mandatory_keys(kwargs)
        cls.validate_entry_point(kwargs)

        name = kwargs["name"]
        supported_variations = kwargs["supported-variations"]
        if type(supported_variations) is str:
            supported_variations = str(supported_variations).split(",")
        supported_variations = [VariationType.resolve(variation.strip()) for variation in supported_variations]
        reference_genome = ReferenceGenome.resolve(kwargs["reference-genome"].strip().lower())
        entry_point = cls.build_entry_point(kwargs)
        manifest_path = kwargs["path"]
        version = kwargs.get("version", None)
        databases = kwargs.get("databases", [])
        cutoff = kwargs.get("cutoff", 0.5)
        supported_chromosomes = kwargs.get("supported-chromosomes", [str(x) for x in range(1, 23)] + ["X", "Y", "MT"])
        unsupported_chromsomes = kwargs.get("unsupported-chromosomes", [])
        supported_chromosomes = set(supported_chromosomes) - set(unsupported_chromsomes)
        p = Plugin(name, version, supported_variations, supported_chromosomes, reference_genome, databases, entry_point,
                   cutoff,
                   manifest_path)
        return p

    @classmethod
    def validate_mandatory_keys(cls, manifest: dict):
        keys = ["name", "supported-variations", "reference-genome", "entry-point"]
        for key in keys:
            if key not in manifest:
                raise RuntimeError(f"Can't build plugin: '{key}' is not specified in manifest {manifest['path']}")

    @classmethod
    def validate_entry_point(cls, manifest: dict):
        entry_point = manifest["entry-point"]
        if "mode" not in entry_point:
            raise RuntimeError(
                f"Can't build plugin: 'mode' for entry-point is not specified in manifest {manifest['path']}")
        mode: str = entry_point["mode"]
        if mode.lower() == "docker":
            keys = ["image", "input", "output", "run"]
            for key in keys:
                if key not in entry_point:
                    raise RuntimeError(
                        f"Can't build plugin: '{key}' is not specified for Docker entry-point of manifest {manifest['path']}")
            for input_output in ["input", "output"]:
                for key in ["format", "file-path"]:
                    if key not in entry_point[input_output]:
                        raise RuntimeError(
                            f"Can't build plugin: '{input_output}/{key}' is not specified for Docker entry-point of "
                            f"manifest {manifest['path']}")
        elif mode.lower() == "python":
            keys = ["file"]
            for key in keys:
                if key not in entry_point:
                    raise RuntimeError(
                        f"Can't build plugin: '{key}' is not specified for Python entry-point of manifest {manifest['path']}")
            pass
        else:
            raise RuntimeError(
                f"Can't build plugin: '{mode}' has to be either 'Docker' or 'Python' for entry-point  in manifest {manifest['path']}")

    @classmethod
    def build_entry_point(cls, manifest):
        mode: str = manifest["entry-point"]["mode"]
        if mode.lower() == "docker":
            return cls.build_docker_entry_point(manifest)
        elif mode.lower() == "python":
            return cls.build_python_entry_point(manifest)

    @classmethod
    def build_docker_entry_point(cls, manifest) -> DockerEntryPoint:
        entry_point = manifest["entry-point"]
        manifest_path = manifest["path"]
        image_name = entry_point["image"]
        run_command = entry_point["run"]
        input_info = entry_point["input"]
        output_info = entry_point["output"]
        bindings = {}
        for local_path, remote_path in entry_point.get("bindings", {}).items():
            local_path = Path(manifest_path).parent.joinpath(local_path).resolve()
            if not local_path.exists():
                raise RuntimeError(
                    f"Cant build entry point for plugin {manifest['name']}: Specified file {local_path} does not exist!")
            bindings[local_path.as_posix()] = remote_path
        return DockerEntryPoint(image_name, run_command, input_info, output_info, bindings)

    @classmethod
    def build_python_entry_point(cls, manifest) -> PythonEntryPoint:
        entry_point = manifest["entry-point"]
        manifest_path = manifest["path"]
        entry_point_file = Path(manifest_path).parent.joinpath(entry_point["file"]).resolve()
        if not entry_point_file.exists():
            raise RuntimeError(
                f"Can't build entry point for plugin {manifest['name']}: Entry point file {entry_point_file} does not exist")
        return PythonEntryPoint(entry_point_file)


@dataclass
class Score:
    """Represent a score from a prioritization method.

    Arguments
    ---------
    plugin
        The method calculated the score
    data
        The calculated scores
    """
    plugin: Plugin
    data: Series

    @property
    def cutoff(self):
        """Get the cutoff from the plugin of the score.

        Returns
        -------
        float
            The cutoff
        """
        return self.plugin.cutoff

    def interpret(self, cutoff: float = None) -> Series:
        """ Interpret the score using the cutoff.

        If the cutoff is None the :meth:`vpmbench.data.Score.cutoff` is used to interpret the score.
        The score is interpreted by replacing all values greater as the cutoff by 1, 0 otherwise.

        Parameters
        ----------
        cutoff
            The cutoff

        Returns
        -------
        :class:`pandas.Series`
            The interpreted scores
        """
        if cutoff is None:
            cutoff = self.cutoff
        return self.data.apply(lambda value: 1 if value > cutoff else 0)
