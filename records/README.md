The catalog includes real research entries and curated examples from public projects.
`last_updated` records when the catalog entry was reviewed or edited; it is not an
upstream release date. GitHub repository timestamps are fetched separately.

Sources for the public examples refreshed on 2026-11-11:

- BERT: https://huggingface.co/google-bert/bert-base-uncased and https://aclanthology.org/N19-1423/
- DistilBERT: https://huggingface.co/distilbert/distilbert-base-uncased and https://arxiv.org/abs/1910.01108
- Vision Transformer: https://huggingface.co/google/vit-base-patch16-224 and https://arxiv.org/abs/2010.11929
- scikit-learn: https://github.com/scikit-learn/scikit-learn and https://jmlr.org/papers/v12/pedregosa11a.html
- Transformers: https://github.com/huggingface/transformers and https://aclanthology.org/2020.emnlp-demos.6/
- PyTorch: https://github.com/pytorch/pytorch and https://arxiv.org/abs/1912.01703

BERT's original training data predates the catalog's Wikipedia 2020 snapshot;
these entries intentionally do not link that snapshot as a training dataset.
Paper years refer to the listed publication venue; stable IDs may retain a
preprint year (for example, `devlin-2018-bert` was published at NAACL in 2019).

Dataset sources added on 2026-11-11:

- IMDb: https://ai.stanford.edu/~amaas/data/sentiment/ and https://huggingface.co/datasets/stanfordnlp/imdb
- SQuAD 1.1: https://rajpurkar.github.io/SQuAD-explorer/ and https://huggingface.co/datasets/rajpurkar/squad
- CIFAR-10: https://www.cs.toronto.edu/~kriz/cifar.html and https://huggingface.co/datasets/uoft-cs/cifar10
- MNIST: https://huggingface.co/datasets/ylecun/mnist

Sizes for these entries describe example counts rather than download sizes.
IMDb has custom usage terms. CIFAR-10's Hub card marks its license as unknown;
the catalog preserves that uncertainty instead of assigning an open license.

Software and published AI papers added on 2026-11-14:

- photosearcher: https://github.com/ropensci-archive/photosearcher/blob/master/DESCRIPTION and https://doi.org/10.1016/j.softx.2020.100624
- viewscape: https://CRAN.R-project.org/package=viewscape and https://doi.org/10.1016/j.softx.2024.101662
- PPGISr: https://github.com/GLISA-umich/PPGISr and https://doi.org/10.1016/j.softx.2023.101389
- bifrost: https://CRAN.R-project.org/package=bifrost and https://jakeberv.com/bifrost/
- Fox et al.: https://researchportal.helsinki.fi/en/publications/balancing-accessibility-and-security-safeguarding-citizen-sourced/ and https://doi.org/10.1016/j.ecoinf.2025.103443
- East et al.: https://doi.org/10.1111/2041-210X.70140
- Jones et al.: https://doi.org/10.1175/BAMS-D-24-0304.1

photosearcher is archived; its original documentation link returned HTTP 404
when reviewed. viewscape's original land-info-lab repository points to
billbillbilly/viewscape, which is also the repository listed by CRAN. Its entry
uses that current source and retains the original repository as a separate link.
SoftwareX publications are linked directly from the software entries.
