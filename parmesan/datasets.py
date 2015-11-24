import numpy as np
import pickle as pkl
import cPickle as cPkl

import gzip
import tarfile
import fnmatch
import os
import urllib
from scipy.io import loadmat
from sklearn.datasets import fetch_lfw_people

def _unpickle(f):
    import cPickle
    fo = open(f, 'rb')
    d = cPickle.load(fo)
    fo.close()
    return d

def _download_frey_faces(dataset):
    """
    Download the MNIST dataset if it is not present.
    :return: The train, test and validation set.
    """
    origin = (
        'http://www.cs.nyu.edu/~roweis/data/frey_rawface.mat'
    )
    print 'Downloading data from %s' % origin
    urllib.urlretrieve(origin, dataset+'.mat')
    matdata = loadmat(dataset)
    f = gzip.open(dataset +'.pkl.gz', 'w')
    pkl.dump([matdata['ff'].T],f)



def _download_mnist_realval(dataset):
    """
    Download the MNIST dataset if it is not present.
    :return: The train, test and validation set.
    """
    origin = (
        'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
    )
    print 'Downloading data from %s' % origin
    urllib.urlretrieve(origin, dataset)

def _download_lwf(dataset,size):
    '''
    :param dataset:
    :return:
    '''
    lfw_people = fetch_lfw_people(color=True,resize=size)
    f = gzip.open(dataset, 'w')
    cPkl.dump([lfw_people.images.astype('uint8'),lfw_people.target],f,protocol=cPkl.HIGHEST_PROTOCOL)
    f.close()


def _download_mnist_binarized(datapath):
    """
    Download the fized binzarized MNIST dataset if it is not present.
    :return: The train, test and validation set.
    """
    datafiles = {
        "train": "http://www.cs.toronto.edu/~larocheh/public/datasets/binarized_mnist/binarized_mnist_train.amat",
        "valid": "http://www.cs.toronto.edu/~larocheh/public/datasets/binarized_mnist/binarized_mnist_valid.amat",
        "test": "http://www.cs.toronto.edu/~larocheh/public/datasets/binarized_mnist/binarized_mnist_test.amat"
    }
    datasplits = {}
    for split in datafiles.keys():
        print "Downloading %s data..." %(split)
        local_file = datapath + '/binarized_mnist_%s.npy'%(split)
        datasplits[split] = np.loadtxt(urllib.urlretrieve(datafiles[split])[0])

    f = gzip.open(datapath +'/mnist.pkl.gz', 'w')
    pkl.dump([datasplits['train'],datasplits['valid'],datasplits['test']],f)


def _get_datafolder_path():
    full_path = os.path.abspath('.')
    path = full_path +'/data'
    return path


def load_mnist_realval(dataset=_get_datafolder_path()+'/mnist_real/mnist.pkl.gz'):
    '''
    Loads the real valued MNIST dataset
    :param dataset: path to dataset file
    :return: None
    '''
    if not os.path.isfile(dataset):
        datasetfolder = os.path.dirname(dataset)
        if not os.path.exists(datasetfolder):
            os.makedirs(datasetfolder)
        _download_mnist_realval(dataset)

    f = gzip.open(dataset, 'rb')
    train_set, valid_set, test_set = pkl.load(f)
    f.close()
    x_train, targets_train = train_set[0], train_set[1]
    x_valid, targets_valid = valid_set[0], valid_set[1]
    x_test, targets_test = test_set[0], test_set[1]
    return x_train, targets_train, x_valid, targets_valid, x_test, targets_test


def load_mnist_binarized(dataset=_get_datafolder_path()+'/mnist_binarized/mnist.pkl.gz'):
    '''
    Loads the fixed binarized MNIST dataset provided by Hugo Larochelle.
    :param dataset: path to dataset file
    :return: None
    '''
    if not os.path.isfile(dataset):
        datasetfolder = os.path.dirname(dataset)
        if not os.path.exists(datasetfolder):
            os.makedirs(datasetfolder)
        _download_mnist_binarized(datasetfolder)

    f = gzip.open(dataset, 'rb')
    x_train, x_valid, x_test = pkl.load(f)
    f.close()
    return x_train, x_valid, x_test


def cifar10(datasets_dir=_get_datafolder_path(), num_val=5000):
    raise Warning('cifar10 loader is untested!')
    # this code is largely cp from Kyle Kastner:
    #
    # https://gist.github.com/kastnerkyle/f3f67424adda343fef40
    try:
        import urllib
        urllib.urlretrieve('http://google.com')
    except AttributeError:
        import urllib.request as urllib
    url = 'http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
    data_file = os.path.join(datasets_dir, 'cifar-10-python.tar.gz')
    data_dir = os.path.join(datasets_dir, 'cifar-10-batches-py')

    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    if not os.path.isfile(data_file):
        urllib.urlretrieve(url, data_file)
        org_dir = os.getcwd()
        with tarfile.open(data_file) as tar:
            os.chdir(datasets_dir)
            tar.extractall()
        os.chdir(org_dir)

    train_files = []
    for filepath in fnmatch.filter(os.listdir(data_dir), 'data*'):
        train_files.append(os.path.join(data_dir, filepath))
    train_files = sorted(train_files, key=lambda x: x.split("_")[-1])

    test_file = os.path.join(data_dir, 'test_batch')

    x_train, targets_train = [], []
    for f in train_files:
        d = _unpickle(f)
        x_train.append(d['data'])
        targets_train.append(d['labels'])
    x_train = np.array(x_train, dtype='uint8')
    shp = x_train.shape
    x_train = x_train.reshape(shp[0] * shp[1], 3, 32, 32)
    targets_train = np.array(targets_train)
    targets_train = targets_train.ravel()

    d = _unpickle(test_file)
    x_test = d['data']
    targets_test = d['labels']
    x_test = np.array(x_test, dtype='uint8')
    x_test = x_test.reshape(-1, 3, 32, 32)
    targets_test = np.array(targets_test)
    targets_test = targets_test.ravel()

    if num_val is not None:
        perm = np.random.permutation(x_train.shape[0])
        x = x_train[perm]
        y = targets_train[perm]

        x_valid = x[:num_val]
        targets_valid = y[:num_val]
        x_train = x[num_val:]
        targets_train = y[num_val:]
        return (x_train, targets_train,
                x_valid, targets_valid,
                x_test, targets_test)
    else:
        return x_train, targets_train, x_test, targets_test



def load_frey_faces(dataset=_get_datafolder_path()+'/frey_faces/frey_faces', normalize=True):
    '''
    Loads the frey faces dataset
    :param dataset: path to dataset file
    '''
    if not os.path.isfile(dataset + '.pkl.gz'):
        datasetfolder = os.path.dirname(dataset+'.pkl.gz')
        if not os.path.exists(datasetfolder):
            os.makedirs(datasetfolder)
        _download_frey_faces(dataset)

    f = gzip.open(dataset+'.pkl.gz', 'rb')
    data = pkl.load(f)[0].astype('float32')
    f.close()
    if normalize:
        data = (data - np.min(data)) / (np.max(data)-np.min(data))
    return data

def load_lfw(dataset=_get_datafolder_path()+'/lfw/lfw', normalize=True,size=0.25):
    '''
    Loads the labelled faces in the wild dataset
    :param dataset: path to dataset file
    '''

    dataset="%s_%0.2f.cpkl"%(dataset,size)
    if not os.path.isfile(dataset):
        datasetfolder = os.path.dirname(dataset)
        if not os.path.exists(datasetfolder):
            os.makedirs(datasetfolder)
        _download_lwf(dataset,size)

    f = gzip.open(dataset, 'rb')
    data = cPkl.load(f)[0].astype('float32')
    f.close()
    if normalize:
        data = data / 256.
    return data


def load_svhn(dataset=_get_datafolder_path()+'/svhn/', normalize=True, extra=False):
    '''
    Loads the street view house numbers dataset
    :param dataset: path to dataset file
    '''
    if not os.path.isfile(dataset +'svhn_train.cpkl'):
        datasetfolder = os.path.dirname(dataset +'svhn_train.cpkl')
        if not os.path.exists(datasetfolder):
            os.makedirs(datasetfolder)
        _download_svhn(dataset)

    with open(dataset +'svhn_train.cpkl', 'rb') as f:
        train_x,train_y = cPkl.load(f)
    with open(dataset +'svhn_test.cpkl', 'rb') as f:
        test_x,test_y = cPkl.load(f)

    if extra:
        with open(dataset +'svhn_extra.cpkl', 'rb') as f:
            extra_x,extra_y = cPkl.load(f)
        train_x = np.concatenate([train_x,extra_x])
        train_y = np.concatenate([train_y,extra_y])

    train_x = train_x.astype('float32')
    test_x = test_x.astype('float32')
    train_y = train_y.astype('int32')
    test_y = test_y.astype('int32')

    if normalize:
        train_x = train_x / 256.
        test_x = test_x / 256.

    return train_x, train_y, test_x, test_y



def _download_svhn(dataset):
    """
    """
    print 'Downloading data from http://ufldl.stanford.edu/housenumbers/, this may take a while...'
    print "Downloading train data..."
    urllib.urlretrieve('http://ufldl.stanford.edu/housenumbers/train_32x32.mat', dataset+'train_32x32.mat')
    print "Downloading test data..."
    urllib.urlretrieve('http://ufldl.stanford.edu/housenumbers/test_32x32.mat', dataset+'test_32x32.mat')
    print "Downloading extra data..."
    urllib.urlretrieve('http://ufldl.stanford.edu/housenumbers/extra_32x32.mat', dataset+'extra_32x32.mat')

    train = loadmat(dataset+'train_32x32.mat')
    train_x = train['X'].swapaxes(2,3).swapaxes(1,2).swapaxes(0,1)
    train_y = train['y'].reshape((-1)) - 1
    test = loadmat(dataset+'test_32x32.mat')
    test_x = test['X'].swapaxes(0,1).swapaxes(2,3).swapaxes(1,2).swapaxes(0,1)
    test_y = test['y'].reshape((-1)) - 1
    extra = loadmat(dataset+'extra_32x32.mat')
    extra_x = extra['X'].swapaxes(0,1).swapaxes(2,3).swapaxes(1,2).swapaxes(0,1)
    extra_y = extra['y'].reshape((-1)) - 1
    print "Saving train data"
    with open(dataset +'svhn_train.cpkl', 'w') as f:
        cPkl.dump([train_x,train_y],f,protocol=cPkl.HIGHEST_PROTOCOL)
    print "Saving test data"
    with open(dataset +'svhn_test.cpkl', 'w') as f:
        pkl.dump([test_x,test_y],f,protocol=cPkl.HIGHEST_PROTOCOL)
    print "Saving extra data"
    with open(dataset +'svhn_extra.cpkl', 'w') as f:
        pkl.dump([extra_x,extra_y],f,protocol=cPkl.HIGHEST_PROTOCOL)
    os.remove(dataset+'train_32x32.mat'),os.remove(dataset+'test_32x32.mat'),os.remove(dataset+'extra_32x32.mat')


# def load_numpy(toFloat=True, binarize_y=False, dtype=np.float32):
#     train = scipy.io.loadmat(path+'/svhn/train_32x32.mat')
#     train_x = train['X'].swapaxes(0,1).T.reshape((train['X'].shape[3], -1)).T
#     train_y = train['y'].reshape((-1)) - 1
#     test = scipy.io.loadmat(path+'/svhn/test_32x32.mat')
#     test_x = test['X'].swapaxes(0,1).T.reshape((test['X'].shape[3], -1)).T
#     test_y = test['y'].reshape((-1)) - 1
#     extra = scipy.io.loadmat(path+'/svhn_extra/extra_32x32.mat')
#     extra_x = extra['X'].swapaxes(0,1).T.reshape((extra['X'].shape[3], -1)).T
#     extra_y = extra['y'].reshape((-1)) - 1
#     if toFloat:
#         train_x = train_x.astype(dtype)/256.
#         test_x = test_x.astype(dtype)/256.
#     if binarize_y:
#         train_y = binarize_labels(train_y)
#         test_y = binarize_labels(test_y)
#
#     return train_x, train_y, test_x, test_y
#
# def load_numpy_extra(toFloat=True, binarize_y=False, dtype=np.float32):
#     extra = scipy.io.loadmat(path+'/svhn_extra/extra_32x32.mat')
#     extra_x = extra['X'].swapaxes(0,1).T.reshape((extra['X'].shape[3], -1)).T
#     extra_y = extra['y'].reshape((-1)) - 1
#     if toFloat:
#         extra_x = extra_x.astype(dtype)/256.
#     if binarize_y:
#         extra_y = binarize_labels(extra_y)
#     return extra_x, extra_y
#
# # Loads data where data is split into class labels
# def load_numpy_split(toFloat=True, binarize_y=False, extra=False):
#
#     train_x, train_y, test_x, test_y = load_numpy(toFloat,binarize_y=False)
#
#     if extra:
#         extra_x, extra_y = load_numpy_extra(toFloat, binarize_y=False)
#         train_x = np.hstack((train_x, extra_x))[:,:604000] #chop off some in the end
#         train_y = np.hstack((train_y, extra_y))[:604000]
#
#     # Make trainingset divisible by 1000
#     keep = int(math.floor(train_x.shape[1]/1000.)*1000)
#     train_x = train_x[:,:keep]
#     train_y = train_y[:keep]
#
#     # Use last n_valid as validation set
#     n_valid = 5000
#     valid_x = train_x[:,-n_valid:]
#     valid_y = train_y[-n_valid:]
#     train_x = train_x[:,:-n_valid]
#     train_y = train_y[:-n_valid]
#
#     def split_by_class(x, y, num_classes):
#         result_x = [0]*num_classes
#         result_y = [0]*num_classes
#         for i in range(num_classes):
#             idx_i = np.where(y == i)[0]
#             result_x[i] = x[:,idx_i]
#             result_y[i] = y[idx_i]
#         return result_x, result_y
#
#     train_x, train_y = split_by_class(train_x, train_y, 10)
#     if binarize_y:
#         test_y = binarize_labels(test_y)
#         valid_y = binarize_labels(valid_y)
#         for i in range(10):
#             train_y[i] = binarize_labels(train_y[i])
#
#     return train_x, train_y, valid_x, valid_y, test_x, test_y