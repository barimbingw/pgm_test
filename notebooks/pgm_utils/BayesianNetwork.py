import numpy as np
import pandas as pd
from itertools import product

class SimpleBN:
    def __init__(self):
        self.Vars = []
        self.Query_Vars = []
        self.Vals = dict()
        self.Factors = dict()

    def add_var_val(self, var_name, var_values=[]):
        self.Vars.append(var_name)
        self.Vals[var_name] = var_values

    def add_factor(self, var_name, CPD, parents=None):
        self.Factors[var_name] = {
            "parents": parents,
            "CPD": self.get_CPD_data_frame(var_name, CPD, parents)
        }

    def id_to_str(self, id):
        return str(id)
    
    def str_to_tuple(self, idstr):
        pass
    
    def get_CPD_data_frame(self, var_name, CPD, parents):
        cols = self.Vals[var_name]
        if parents is None:
            d = pd.Series(CPD, index=cols)
            assert d.sum()==1.0, f"CPD for variable {var_name} not added up to 1"
            return d
        if isinstance(parents, str):
            parents = [parents]
        rows = [self.id_to_str(el) for el in product(*[self.Vals[p] for p in parents])]
        d = pd.DataFrame(CPD, index=rows, columns=cols)
        assert np.all(d.sum(axis=1)==1.0), f"CPD for variable {var_name} not added up to 1"
        return d
    
    def get_factor_value(self, var_name, var_val, given=dict()):
        parents = self.Factors[var_name]["parents"]
        if parents is None:
            return self.Factors[var_name]["CPD"][var_val]
        return self.Factors[var_name]["CPD"].loc[self.id_to_str(tuple([given[p] for p in parents])), var_val]
    
    def get_prob_sub(self, query):
        # print(query)
        res = 1
        for v in self.Query_Vars:
            val = query[v]
            res *= self.get_factor_value(v, val, given=query)
        return res

    def get_table(self, event, evidence=dict()):
        if isinstance(event, str):
            observation = [event]
        joint_vars = event + list(evidence.keys())
        eliminated_vars = [v for v in self.Vars if v not in joint_vars]
        # related_vars = []
        # for v in eliminated_vars:
        #     parents = self.Factors[v]["parents"]
        #     if parents is None:
        #         continue
        #     if isinstance(parents, str):
        #         parents = [parents]
        #     for p in parents:
        #         if p in joint_vars:
        #             related_vars.append(v)
        #             break

        # self.Query_Vars = set(joint_vars + related_vars)
        self.Query_Vars = self.Vars

        result = []
        if eliminated_vars==[]:
            for ele in product(*[self.Vals[o] for o in event]):
                query = dict([(ovar, oval) for ovar, oval in zip(event, ele)])
                if len(evidence)>0:
                    for evar in evidence.keys():
                        query[evar] = evidence[evar]
                result.append(self.get_prob_sub(query))
        else:
            for ele in product(*[self.Vals[o] for o in event]):
                query = dict([(ovar, oval) for ovar, oval in zip(event, ele)])
                if len(evidence)>0:
                    for evar in evidence.keys():
                        query[evar] = evidence[evar]
                temp = 0
                # print('----------------')
                for elel in product(*[self.Vals[e] for e in eliminated_vars]):
                    for i, e in enumerate(eliminated_vars):
                        query[e] = elel[i]
                    r = self.get_prob_sub(query)
                    # print(query, r, temp+r)
                    temp += r
                result.append(temp)
        
        result = pd.Series(result, index=product(*[self.Vals[o] for o in event]))
        return result/result.sum()