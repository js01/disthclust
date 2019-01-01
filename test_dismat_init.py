import numpy as np
from multiprocessing import Process
import server3 as s3
import server3_test_functions as s3tf
from blockfilemmap import *
from linkage_functions import *
from worker3 import *

n = 37
d = 532
X = np.random.randint(0,2,(n,d),dtype='uint8')
print(X)
print()

constants.init(n,d)
nb, bs = constants.N_BLOCK, constants.BLOCK_SIZE

sp = Process(target=s3tf.test_dismat_init, args=(X, "test_block_files", "test_data",))
sp.start()
print("Test: server initialized")
workers = [CoreServer(n, d, "test_block_files", "test_data") for i in range(1)]
procs = [Process(target=workers[i].listen, args=()) for i in range(len(workers))]
print("Test: workers initialized")
[p.start() for p in procs]
print("joining the processes")
print("testing")
bdist = np.zeros((constants.N_BLOCK,constants.N_BLOCK),dtype=object)
base_directory = "test_block_files"
time.sleep(5)
dm = np.zeros((len(X), len(X)))
for i in range(len(dm)-1):
    for j in range(i+1, len(dm)):
        dmi = X[i]
        dmj = X[j]
        ne = np.not_equal(dmj,dmi).astype(int)
        dm[i][j] = sum(ne)
dm = dm.astype(int)

print(dm)
for bi in range(constants.N_BLOCK):
    for bj in range(bi, constants.N_BLOCK):
        bfd = base_directory+"/{}_d/{}_d.block".format(bi, bj)
        print(bfd)

#        bshape = constants.getbshape(bi, bj)
        bshape = (constants.BLOCK_SIZE, constants.BLOCK_SIZE)

        dist_block = BlockFileMap(bfd, constants.DATA_TYPE, bshape)
        dist_block.open()
        block = dist_block.read_all()
        nbil = bi * constants.BLOCK_SIZE
        nbir = (bi+1) * constants.BLOCK_SIZE
        nbjl = bj * constants.BLOCK_SIZE
        nbjr = (bj+1) * constants.BLOCK_SIZE
        dmblock = dm[nbil:nbir, nbjl:nbjr]
        print("read", block)
        print("true", dmblock)
        for i in range(len(dmblock)):
            for j in range(len(dmblock[i])):
                assert dmblock[i,j] == block[i,j]
        dist_block.close()

print("Tests passed!")




[p.join() for p in procs]