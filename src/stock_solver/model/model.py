import torch
import argparse

parser = argparse.ArgumentParser()



class StockSolver(torch.nn.Module):    
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x

if __name__ == '__main__':
    args = parser.parse_args([] if  "__file__" not in globals() else None)