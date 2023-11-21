import json
import numpy as np

def main():
    print("main")
    with open('./input.json') as f:
        model = json.load(f)
    print(model["coords"])
    x = np.array([e[0] for e in model["coords"]])
    print(x)
    y = np.array([e[1] for e in model["coords"]])
    print(y)

    #constantes
    m = 7850
    k = 210000000000
    r = 1
    Np = x.shape[0]
    N = 100
    forces = [
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [0,0],
        [-1000,0],
        [-1000,0],
        [-1000,0],
    ]

    f = np.array([e[0] for e in forces])
    f = np.reshape(f, 2*Np, 1)
    print(f)

    #condicoes iniciais
    u = np.zeros(2*Np)
    v = np.zeros(2*Np)

    a = np.ones(2*Np)*(1/m)*f

    for i in range(N):
        print(i)

    

if __name__ == '__main__':
    main()