import pickle
import hashlib


def md5(obj):
    return int(hashlib.md5(pickle.dumps(obj)).hexdigest(), 16)


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


def sha224(obj):
    return int(hashlib.sha224(pickle.dumps(obj)).hexdigest(), 16)


def sha256(obj):
    return int(hashlib.sha256(pickle.dumps(obj)).hexdigest(), 16)


def sha384(obj):
    return int(hashlib.sha384(pickle.dumps(obj)).hexdigest(), 16)


def sha512(obj):
    return int(hashlib.sha512(pickle.dumps(obj)).hexdigest(), 16)
