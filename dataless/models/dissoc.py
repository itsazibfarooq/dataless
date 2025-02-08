import matplotlib.pyplot as plt 
import networkx as nx 
from torch import nn 
import torch 

class Hadamard(nn.Module):
    def __init__(self, in_feature, low_bound:int=0, up_bound:int=1):
        super().__init__()
        self.low_bound = low_bound 
        self.up_bound = up_bound
        self.weight = nn.Parameter(torch.Tensor(in_feature))
    
    def forward(self, x):
        self.weight.data = self.weight.data.clamp(self.low_bound, self.up_bound)
        return x * self.weight
    
class DISSOC(nn.Module):
    def __init__(self, G, theta_init=None):
        super().__init__()
        self.graph = G
        self.n = len(self.graph.nodes)
        self.three_paths = self.three_path()
        self.m = len(self.three_paths)

        self.temperature = 0.5
        self.theta_init = theta_init

        self.theta_layer = Hadamard(self.n)
        self.theta_layer.weight = self.theta_weight()

        self.layer2 = nn.Linear(in_features=self.n, out_features=self.n + self.m)
        self.layer2.weight = self.layer2_weight()
        self.layer2.bias = self.layer2_bias()

        self.layer3 = nn.Linear(in_features=self.n + self.m, out_features=1, bias=False)
        self.layer3.weight = self.layer3_weight()
        
        self.layer2.weight.requires_grad_(False) 
        self.layer2.bias.requires_grad_(False)
        self.layer3.weight.requires_grad_(False)

        self.activation = nn.ReLU()

    def forward(self, x):
        with torch.no_grad():
            self.layer2.bias.data[0 : self.n] = -1.0 * self.temperature

        x = self.theta_layer(x)
        x = self.layer2(x)
        x = self.activation(x)
        x = self.layer3(x)
        return x 

    def theta_weight(self):
        """ theta parameter vector """
        g = torch.manual_seed(123)
        theta_weight = torch.rand((self.n), generator=g)

        if self.theta_init:
            theta_weight = theta_weight * 0.5
            theta_weight[self.theta_init] = 0.6 + theta_weight[self.theta_init] * 0.2
        return nn.Parameter(theta_weight)

    def layer2_weight(self):
        """ W matrix derived from G """
        W = torch.zeros([self.n, self.n + self.m])
        W[:, :self.n] = torch.eye(self.n)

        for idx, e in enumerate(self.three_paths):
            W[:, self.n + idx] = self.one_hot(list(e))

        return nn.Parameter(W.T.to_dense())

    def layer2_bias(self):
        """ b vector derived from G """
        bias = torch.zeros(self.n + self.m) - 2
        bias[:self.n] = -0.75

        return nn.Parameter(bias)

    def layer3_weight(self):
        """ w vector derived from G """
        w = torch.zeros(self.n + self.m) + -1.0
        w[self.n:] = self.n
        
        return nn.Parameter(w.to_dense())
    
    def trainable_params(self):
        """ Counting trainable parameters """
        params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f'trainable params: {params}')
        return params
    
    def one_hot(self, arr):
        res = torch.zeros(self.n)
        res[arr] = 1
        return res

    def three_path(self):
        paths = []
        for v in self.graph.nodes():
            neighbors = list(G.neighbors(v))
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u, w = neighbors[i], neighbors[j]
                    paths.append((u, v, w))                      
        return paths

    def plot(self):
        plt.figure(figsize=(6, 4))
        nx.draw(self.graph, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='gray')
        plt.show()
    
    def vanilla_eq(self):
        pass
    
if __name__ == '__main__':
    G = nx.Graph()
    G.add_nodes_from(list(range(5)))
    edges = [(0,1),(1,2),(2,3),(3,4),(0,4)] 
    G.add_edges_from(edges) 
    
    model = Net(G, theta_init=torch.Tensor([1,0,0,0,0]))
    # print(model.theta_layer.weight)
    print(model(torch.ones(len(G.nodes))))
    print(model.layer2.weight.data.T, model.layer2.bias.data, model.layer3.weight.data)
    # model.trainable_params()
    # model.plot()






