import multiprocessing as mp
from opensimplex import OpenSimplex
from noise import pnoise2, snoise2
import numpy as np
import time


class A(object):
    def __init__(self, *args, **kwargs):
        self.MAP_SIZE = 1024
        self.noise_map = np.empty((self.MAP_SIZE, self.MAP_SIZE), dtype=np.float)
        self.time = None

    # PNOISE2
    def make_noise_perlin(self):
        start_time = time.time()
        for x in range(self.MAP_SIZE):
            for y in range(self.MAP_SIZE):
                self.noise_map[x][y] = pnoise2(x, y,
                                               octaves=6, persistence=0.5,
                                               repeatx=self.MAP_SIZE, repeaty=self.MAP_SIZE, base=0)
        print("Pnoise2 norm. time:  %.4f seconds" % (time.time() - start_time))

    def fast_perlin(self, x):
        noise_table = []
        factor_x = x / 32
        for y in range(self.MAP_SIZE):
            noise_value = pnoise2(factor_x, y / 32,
                                  octaves=6, persistence=0.5,
                                  repeatx=self.MAP_SIZE, repeaty=self.MAP_SIZE, base=0)
            noise_table.append(noise_value)
        return noise_table

    def run_perlin(self, cores):
        p = mp.Pool(cores)
        start_time = time.time()
        self.noise_map = p.map(self.fast_perlin, range(self.MAP_SIZE))
        #p.close
        print("Pnoise2 multi time ({0} cores):  {1:.3f} seconds".format(cores, (time.time() - start_time)))
        self.time = (time.time() - start_time)

    # SNOISE2
    def make_noise_simplex(self):
        start_time = time.time()
        for x in range(self.MAP_SIZE):
            factor_x = x / 32
            for y in range(self.MAP_SIZE):
                self.noise_map[x][y] = snoise2(factor_x, y/32,
                                               octaves=6, persistence=0.5,
                                               repeatx=self.MAP_SIZE, repeaty=self.MAP_SIZE, base=0)
        #print("Snoise2 norm. time:  %.3f seconds" % (time.time() - start_time))
        self.time = (time.time() - start_time)

    def fast_simplex(self, x):
        noise_table = []
        factor_x = x / 32
        for y in range(self.MAP_SIZE):
            noise_table.append(snoise2(factor_x, y / 32,
                                       octaves=6, persistence=0.5,
                                       repeatx=self.MAP_SIZE, repeaty=self.MAP_SIZE, base=0))
        return noise_table

    def run_simplex(self, cores):
        p = mp.Pool(cores)
        start_time = time.time()
        self.noise_map = p.map(self.fast_simplex, range(self.MAP_SIZE))
        #p.close
        #print("Snoise2 multi time ({0} cores):  {1:.3f} seconds".format(cores, (time.time() - start_time)))
        self.time = (time.time() - start_time)

    # Opensimplex
    def make_noise_opensimplex(self):
        os_noise = OpenSimplex()
        start_time = time.time()
        for x in range(self.MAP_SIZE):
            for y in range(self.MAP_SIZE):
                noise_value = os_noise.noise2d(x / 32, y / 32)
                self.noise_map[x][y] = noise_value
        print("Opensimplex norm time:  %.3f seconds" % (time.time() - start_time))
        self.time = (time.time() - start_time)

    def fast_opensimplex(self, x):
        noise_table = []
        os_noise = OpenSimplex()
        factor_x = x / 40
        for y in range(self.MAP_SIZE):
            noise_value = os_noise.noise2d(factor_x, y / 40)
            noise_table.append(noise_value)
        return noise_table

    def run_multi(self):
        start_time = time.time()
        p = Pool()
        self.noise_map = p.map(self.fast_opensimplex, range(self.MAP_SIZE))
        #p.close
        print("Opensimplex multi time:  %.3f seconds" % (time.time() - start_time))
        self.time = (time.time() - start_time)


if __name__ == '__main__':
    a = A()
    #a.MAP_SIZE = 1000
    """
    a.noise_map = np.empty((a.MAP_SIZE, a.MAP_SIZE), dtype=np.float)
    a.make_noise_perlin()
    a.noise_map = np.empty((a.MAP_SIZE, a.MAP_SIZE), dtype=np.float)
    a.run_perlin()
    a.noise_map = np.empty((a.MAP_SIZE, a.MAP_SIZE), dtype=np.float)
    a.make_noise_simplex()
    """
    for size in range(400, 401, 100):
        print("Table size: %s^2" % size)
        a.MAP_SIZE = size
        sum = 0
        for i in range(1):
            a.noise_map = np.empty((a.MAP_SIZE, a.MAP_SIZE), dtype=np.float)
            a.make_noise_simplex()
            sum += a.time
        print("Average time for 1 core: {0:.3f} s".format(sum/10))
        for core in range(4, 5):
            sum = 0
            for i in range(1):
                a.noise_map = np.empty((a.MAP_SIZE, a.MAP_SIZE), dtype=np.float)
                a.run_simplex(core)
                sum += a.time
            print("Average time for {0} cores: {1:.3f} s".format(core, sum/10))
    # Opensimplex is too slow even with multiprocessing
    #a.make_noise_opensimplex()
    #a.run_multi()

