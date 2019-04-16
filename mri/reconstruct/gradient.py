# -*- coding: utf-8 -*-
##########################################################################
# pySAP - Copyright (C) CEA, 2017 - 2018
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains classes for defining algorithm operators and gradients.
"""


# Third party import
import numpy as np
from modopt.math.matrix import PowerMethod
from modopt.opt.gradient import GradBasic, GradParent


class GradAnalysis2(GradBasic, PowerMethod):

    def __init__(self, data, fourier_op):

        GradBasic.__init__(self, data, fourier_op.op, fourier_op.adj_op)
        self.fourier_op = fourier_op
        PowerMethod.__init__(self, self.trans_op_op, self.fourier_op.shape,
                             data_type=np.complex, auto_run=False)
        self.get_spec_rad(extra_factor=1.1)


class GradProxDual(GradParent, PowerMethod):

    def __init__(self, data, wav_op, shape):

        GradParent.__init__(self, data, wav_op.adj_op, wav_op.op)
        self.wav_op = wav_op
        self.get_grad = self._get_grad_method
        self.cost = self._cost_method
        PowerMethod.__init__(self, self.trans_op_op, shape,
                             data_type=np.complex, auto_run=False)
        self.get_spec_rad(extra_factor=1.1)

    def _get_grad_method(self, data):
        self.grad = self.trans_op_op(data) + self.obs_data

    def _cost_method(self, data):
        return 0.5 * np.linalg.norm(self.op(data)) + np.vdot(data, self.obs_data)


class GradSynthesis2(GradBasic, PowerMethod):

    def __init__(self, data, linear_op, fourier_op):

        GradBasic.__init__(self, data, self._op_method, self._trans_op_method)
        self.fourier_op = fourier_op
        self.linear_op = linear_op
        coef = linear_op.op(np.zeros(fourier_op.shape).astype(np.complex))
        PowerMethod.__init__(self, self.trans_op_op, coef.shape,
                             data_type=np.complex, auto_run=False)
        self.get_spec_rad(extra_factor=1.1)

    def _op_method(self, data, *args, **kwargs):

        return self.fourier_op.op(self.linear_op.adj_op(data))

    def _trans_op_method(self, data, *args, **kwargs):

        return self.linear_op.op(self.fourier_op.adj_op(data))
