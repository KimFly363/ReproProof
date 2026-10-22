"""Catalog of common ML datasets and metrics for limited paper-code matching."""
from __future__ import annotations


DATASET_ALIASES = {
    "CIFAR-10": ["cifar-10", "cifar10"],
    "CIFAR-100": ["cifar-100", "cifar100"],
    "ImageNet": ["imagenet", "ilsvrc"],
    "COCO": ["coco", "ms coco", "mscoco"],
    "Flickr30K": ["flickr30k", "flickr 30k"],
    "MNIST": ["mnist"],
    "Fashion-MNIST": ["fashion-mnist", "fashionmnist", "fashion mnist"],
    "CelebA": ["celeba"],
    "Pascal VOC": ["pascal voc", "voc2012", "voc 2012"],
    "Cityscapes": ["cityscapes"],
    "GLUE": ["glue benchmark", "glue"],
    "SQuAD": ["squad"],
    "WikiText": ["wikitext"],
    "MultiVLM-12": ["multivlm-12", "multivlm12"],
}

METRIC_ALIASES = {
    "accuracy": ["accuracy", "acc", "准确率", "准确度"],
    "F1": ["f1-score", "f1 score", "f1", "f1值"],
    "precision": ["precision", "精确率", "查准率"],
    "recall": ["recall", "召回率", "查全率"],
    "mAP": ["map", "mean average precision", "平均精度均值"],
    "AUC": ["auc", "roc-auc", "roc auc"],
    "BLEU": ["bleu"],
    "ROUGE": ["rouge"],
    "PSNR": ["psnr"],
    "SSIM": ["ssim"],
    "RMSE": ["rmse"],
    "MAE": ["mae"],
}

CODE_DATASET_HINTS = {
    "CIFAR-10": ["cifar-10", "cifar10", "cifar_10"],
    "CIFAR-100": ["cifar-100", "cifar100", "cifar_100"],
    "ImageNet": ["imagenet", "ilsvrc"],
    "COCO": ["coco"],
    "Flickr30K": ["flickr30k", "flickr_30k", "flickr-30k"],
    "MNIST": ["mnist"],
    "Fashion-MNIST": ["fashion_mnist", "fashionmnist"],
    "CelebA": ["celeba"],
    "Pascal VOC": ["voc2012", "pascal_voc"],
    "Cityscapes": ["cityscapes"],
    "GLUE": ["glue"],
    "SQuAD": ["squad"],
    "WikiText": ["wikitext"],
    "MultiVLM-12": ["multivlm_12", "multivlm12"],
}

CODE_METRIC_HINTS = {
    "accuracy": ["accuracy_score", "accuracy(", "acc=", "acc ="],
    "F1": ["f1_score", "f1-score", "f1("],
    "precision": ["precision_score", "precision("],
    "recall": ["recall_score", "recall("],
    "mAP": ["average_precision_score", "map(", "mAP"],
    "AUC": ["roc_auc_score", "auc("],
    "BLEU": ["bleu", "sacrebleu"],
    "ROUGE": ["rouge"],
    "PSNR": ["psnr"],
    "SSIM": ["ssim"],
    "RMSE": ["mean_squared_error", "rmse"],
    "MAE": ["mean_absolute_error", "mae"],
}
