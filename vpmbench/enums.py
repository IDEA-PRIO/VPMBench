from enum import Enum


# class PathogencityClass(Enum):
#     """ Represent the pathogencity classes of the variants.
#
#     Following values are supported:
#
#         * BENIGN for benign variants
#         * PATHOGENIC for pathogenic variants
#     """
#
#     BENIGN = "benign"
#     PATHOGENIC = "pathogenic"
#
#     def interpret(self) -> int:
#         """ Interpret the pathogencity class to get a numerical value.
#
#         The following rules apply:
#
#             * ``PathogencityClass.BENIGN`` -> 0
#             * ``PathogencityClass.PATHOGENIC`` -> 1
#
#         Returns
#         -------
#         int
#             The interpreted value of the pathogencity class
#         """
#         if self == PathogencityClass.PATHOGENIC:
#             return 1
#         else:
#             return 0
#
#     @staticmethod
#     def resolve(name: str) -> 'PathogencityClass':
#         """ Return a pathogencity based on the given string
#         The following rules apply:
#             * if 'benign' in name -> ``PathogencityClass.BENIGN``
#             * if 'pathogenic' in name -> ``PathogencityClass.PATHOGENIC``
#         Parameters
#         ----------
#         name :
#             The string.
#         Returns
#         -------
#         PathogencityClass
#             The resulting pathogencity class for the string
#         Raises
#         ------
#         RuntimeError
#             If the name can not be resolved
#         """
#         if "benign" in name or "2" in name:
#             return PathogencityClass.BENIGN
#         elif "pathogenic" in name or "5" in name:
#             return PathogencityClass.PATHOGENIC
#         else:
#             raise RuntimeError(f"Can't resolve pathogencity class for name '{name}'")
#
#     def __str__(self):
#         return self.value


class VariationType(Enum):
    """ Represent the variation types of the variants.

    Following values are supported:

        * SNP for single-nucleotide polymorphism
        * INDEL for insertions or deletions
    """
    SNP = "snp"
    INDEL = "indel"
    CODING = "conding"
    NON_CODING = "non-coding"

    @staticmethod
    def resolve(name: str) -> 'VariationType':
        """ Return the variation type based on the given string

        The following rules apply:

            * if name.lower() == 'snp' -> ``VariationType.SNP``
            * if name.lower() == 'indel' -> ``VariationType.INDEL``

        Parameters
        ----------
        name :
            The string

        Returns
        -------
        VariationType
            The variation type

        Raises
        ------
        RuntimeError
            If the name can not be solved
        """
        name = name.lower()
        rv = VariationType(name)
        if rv is not None:
            return rv
        else:
            raise RuntimeError(f"Can't resolve variation type for name {name}")

    def __str__(self):
        return self.value


class ReferenceGenome(Enum):
    """ Represent reference genomes.

    Following values are supported:

        * HG38
        * HG19
        * HG18
        * HG17
        * HG16

    """
    HG38 = "hg38"
    HG19 = "hg19"
    HG18 = "hg18"
    HG17 = "hg17"
    HG16 = "hg16"

    @staticmethod
    def resolve(name: str) -> 'ReferenceGenome':
        """ Resolve string into a reference genome.

        The following rules apply:

            * if "grch38" in name.lower() -> ``ReferenceGenome.HG38``
            * if "grch37" in name.lower() -> ``ReferenceGenome.HG19``
            * otherwise: ``ReferenceGenome(name)`` is called

        Parameters
        ----------
        name :
            The string.

        Returns
        -------
        ReferenceGenome
            The reference genome

        Raises
        ------
        RuntimeError
            If the name can not be solved
        """
        name = name.lower()
        try:
            if "grch38" in name:
                return ReferenceGenome.HG38
            elif "grch37" in name:
                return ReferenceGenome.HG19
            else:
                return ReferenceGenome(name)
        except Exception:
            raise RuntimeError(f"Can't resolve reference genome for name {name}")

    def __str__(self):
        return self.value
