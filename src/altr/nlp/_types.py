from typing import TypeAlias
from dataclasses import dataclass

Text: TypeAlias = str
Token: TypeAlias = str  # token is just a word, but in the LLM context, it might not be a human readable word
Word: TypeAlias = str  # human readable word


@dataclass
class NgramInfo:
    """Information about n-grams at a specific level.

    Fields:
        n: The n-gram level (1=unigram, 2=bigram, 3=trigram, etc.)
        tokenised_texts: All tokenised texts accumulated up to this n-gram level (cumulative).
            Includes tokens from all previous n-gram levels plus the current one.
        filtered_ngram_tokenised_texts: Tokenised texts for only this specific n-gram level.
            Filtered to just the current level, not cumulative.
        model: Optional trained model for this n-gram level (None for n=1).

    Example:
        Given input texts: ["machine learning model", "deep learning model"]

        n=1 (unigrams):
            tokenised_texts: [
                ["machine", "learning", "model"],
                ["deep", "learning", "model"]
            ]
            filtered_ngram_tokenised_texts: [
                ["machine", "learning", "model"],
                ["deep", "learning", "model"]
            ]
            model: None

        n=2 (bigrams):
            Assume the model found that "machine learning" and "deep learning"
            frequently appear together and should be joined with delimiter "_".

            tokenised_texts: [
                # Original tokens replaced with connected bigrams where applicable
                ["machine_learning", "model"],
                ["deep_learning", "model"]
            ]
            filtered_ngram_tokenised_texts: [
                # Only the new bigram tokens
                ["machine_learning"],
                ["deep_learning"]
            ]
            model: <trained bigram model>

        n=3 (trigrams):
            tokenised_texts: [
                # Tokens with connected trigrams where applicable
                ["machine_learning_model"],
                ["deep_learning_model"]
            ]
            filtered_ngram_tokenised_texts: [
                # Only the new trigram tokens (if any)
                ["machine_learning_model"],
                ["deep_learning_model"]
            ]
            model: <trained trigram model>
    """

    n: int
    tokenised_texts: list[list[Token]]
    filtered_ngram_tokenised_texts: list[list[Token]]
    model: object | None = None

    def ngram_name(self) -> str:
        if self.n == 1:
            return "unigram"
        elif self.n == 2:
            return "bigram"
        elif self.n == 3:
            return "trigram"
        else:
            return f"{self.n}-gram"

    def __repr__(self) -> str:
        return (
            f"NgramInfo(n={self.n}, "
            f"tokenised_texts=[...{len(self.tokenised_texts)} items...], "
            f"filtered_ngram_tokenised_texts=[...{len(self.filtered_ngram_tokenised_texts)} items...], "
            f"model={self.model!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class NgramContext:
    """Context containing n-gram information for multiple n-gram levels.

    Fields:
        ns: Dictionary mapping n-gram level (n) to its corresponding NgramInfo.
            Example: {1: NgramInfo(...), 2: NgramInfo(...), 3: NgramInfo(...)}
    """

    ns: dict[int, NgramInfo]

    def __repr__(self) -> str:
        lines = ["NgramContext("]
        for n, info in self.ns.items():
            lines.append(f"  {info.ngram_name()} (n={n}):")
            lines.append(f"    tokenised_texts        = [...{len(info.tokenised_texts)} items...]")
            lines.append(f"    filtered_ngram_tokens  = [...{len(info.filtered_ngram_tokenised_texts)} items...]")
            lines.append(f"    model                  = {info.model!r}")
        lines.append(")")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.__repr__()

    def get(self, n: int) -> NgramInfo | None:
        """Get the NgramInfo for a specific n-gram level."""
        return self.ns.get(n)
