import numpy as np
from scipy.linalg import norm
from scipy.signal import hilbert
from convolutions import ConvolutionNeuromag
from itertools import combinations
from Data import Data
import matplotlib



def get_convovled_data(data,convolutions):
    for conv in convolutions:
        yield data[:,conv,:]

class AlexPreprocess:
    def __init__(self,sensor_type, conv_length):
        self.conv_length=conv_length
        data_object = Data()                    #TODO remove data from instanse variables
        self.data = data_object.get_data()
        conv_object = ConvolutionNeuromag(sensor_type)
        self.convolution_indeces = conv_object.get_1Dconvolution_channels(conv_length)

    def extract_expert_features(self):
        phase_data = self._calc_local_phase()
        beta = 0.8
        features_length,time_length = len(self.convolution_indeces),self.data.shape[2]
        res = np.zeros((features_length,time_length))
        for index, data_chunk4conv in enumerate(get_convovled_data(phase_data,self.convolution_indeces)):
            res[index,:]=self._get_Alex_feature(data_chunk4conv, beta)
        return res



    def _calc_local_phase(self):            #TODO rewrite as generators for large amount of data
        analytic_signal = hilbert(self.data)
        return np.unwrap(np.angle(analytic_signal))


    def _get_Alex_feature(self,conv_phase_values,beta):
        conv_phase_delta = [i-j for i,j in combinations(conv_phase_values,2)] # calc phase deltas between sensors in convol.
        return np.exp(-beta * norm(conv_phase_delta) ** 2)


    def visualise_activations(self,vis_object):
        extracted_features = self.extract_expert_features()
        norm = matplotlib.colors.Normalize(vmin=extracted_features.min(), vmax=extracted_features.min())

        for t in xrange(extracted_features.shape[1]):
            title = 'Time %f' %t
            vis_object._visualise_target_convolutions(self.convolution_indeces,norm(extracted_features[:,t]), title)



if __name__ == '__main__':
    tmp = AlexPreprocess('mag',3)
    result = tmp.extract_expert_features()
    print result