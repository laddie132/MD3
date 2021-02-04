#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Han"
__email__ = "liuhan132@foxmail.com"

import os
import sys
import yaml
import json
import torch.multiprocessing
from torch.utils.tensorboard import SummaryWriter
import logging
import logging.config
from utils.functions import set_seed

logger = logging.getLogger(__name__)


def init_env(config_path, in_infix, out_infix, writer_suffix, gpuid):
    logger.info('loading config file...')
    game_config = read_config(config_path, in_infix, out_infix)

    # config in logs
    logger.debug(json.dumps(game_config, indent=2))

    # set multi-processing: bugs in `list(dataloader)`
    # see more on `https://github.com/pytorch/pytorch/issues/973`
    torch.multiprocessing.set_sharing_strategy('file_system')

    # set random seed
    set_seed(game_config['global']['random_seed'])

    # gpu
    enable_cuda = torch.cuda.is_available() and gpuid is not None
    device = torch.device("cuda" if enable_cuda else "cpu")
    if enable_cuda:
        torch.cuda.set_device(gpuid)
        torch.backends.cudnn.deterministic = True
    logger.info("CUDA #{} is avaliable".format(gpuid)
                if enable_cuda else "CUDA isn't avaliable")

    # summary writer
    writer = SummaryWriter(log_dir=game_config['checkpoint'][writer_suffix])

    return game_config, enable_cuda, device, writer


def init_logging(config_path='config/logging_config.yaml', out_infix='default'):
    """
    initial logging module with config
    :param out_infix:
    :param config_path:
    :return:
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.Loader)

        out_prefix = 'outputs/' + out_infix + '/'
        if not os.path.exists(out_prefix):
            os.makedirs(out_prefix)

        config['handlers']['info_file_handler']['filename'] = out_prefix + 'debug.log'
        config['handlers']['time_file_handler']['filename'] = out_prefix + 'debug.log'
        config['handlers']['error_file_handler']['filename'] = out_prefix + 'error.log'

        logging.config.dictConfig(config)
    except IOError:
        sys.stderr.write('logging config file "%s" not found' % config_path)
        logging.basicConfig(level=logging.DEBUG)


def read_config(config_path='config/game_config.yaml', in_infix='default', out_infix='default'):
    """
    store the global parameters in the project
    :param in_infix:
    :param out_infix:
    :param config_path:
    :return:
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.Loader)

        out_prefix = 'outputs/' + out_infix + '/'
        if not os.path.exists(out_prefix):
            os.makedirs(out_prefix)

        in_prefix = 'outputs/' + in_infix + '/'
        # assert os.path.exists(in_prefix)

        checkpoint = {'dialog_data_path': out_prefix + 'dialog_data.json',
                      'false_dialog_data_path': out_prefix + 'dialog_data_false.json',
                      'main_log_path': out_prefix + 'main_logs',
                      'state_log_path': out_prefix + 'state_logs',
                      'in_state_weight_path': in_prefix + 'state_weight.pt',
                      'in_state_checkpoint_path': in_prefix + 'state_checkpoint',
                      'out_state_weight_path': out_prefix + 'state_weight.pt',
                      'out_state_checkpoint_path': out_prefix + 'state_checkpoint',
                      'policy_log_path': out_prefix + 'policy_logs',
                      'in_policy_weight_path': in_prefix + 'policy_weight.pt',
                      'in_policy_checkpoint_path': in_prefix + 'policy_checkpoint',
                      'out_policy_weight_path': out_prefix + 'policy_weight.pt',
                      'out_policy_checkpoint_path': out_prefix + 'policy_checkpoint',
                      'mrc_log_path': out_prefix + 'mrc_logs',
                      'in_mrc_weight_path': in_prefix + 'mrc_weight.pt',
                      'in_mrc_checkpoint_path': in_prefix + 'mrc_checkpoint',
                      'out_mrc_weight_path': out_prefix + 'mrc_weight.pt',
                      'out_mrc_checkpoint_path': out_prefix + 'mrc_checkpoint',
                      'pt_log_path': out_prefix + 'pt_logs',
                      'in_pt_weight_path': in_prefix + 'pt_weight.pt',
                      'in_pt_checkpoint_path': in_prefix + 'pt_checkpoint',
                      'out_pt_weight_path': out_prefix + 'pt_weight.pt',
                      'out_pt_checkpoint_path': out_prefix + 'pt_checkpoint'}

        config['checkpoint'] = checkpoint

        # add prefix to dataset path
        data_prefix = config['dataset']['data_prefix']
        config['dataset']['vocab_path'] = data_prefix + config['dataset']['vocab_path']
        config['dataset']['embedding_path'] = data_prefix + config['dataset']['embedding_path']
        config['dataset']['doc_id_path'] = data_prefix + config['dataset']['doc_id_path']
        config['dataset']['cand_doc_path'] = data_prefix + config['dataset']['cand_doc_path']

        return config

    except IOError:
        sys.stderr.write('logging config file "%s" not found' % config_path)
        exit(-1)
