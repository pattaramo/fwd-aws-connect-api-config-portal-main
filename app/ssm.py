import boto3
import os
import json
from aws_lambda_powertools import Logger

logger = Logger()

client = boto3.client('ssm')


class SsmConfig:

    def get_config(self):
        return self.config

    def load_config(self, ssm_parameter_path):
        """
        Load configparser from config stored in SSM Parameter Store
        :param ssm_parameter_path: Path to app config in SSM Parameter Store
        :return: ConfigParser holding loaded config
        """
        configuration = {}
        try:
            # Get all parameters for this app
            param_details = client.get_parameters_by_path(
                Path=ssm_parameter_path, Recursive=False, WithDecryption=True)

            # Loop through the returned parameters and populate the ConfigParser
            if 'Parameters' in param_details and len(
                    param_details.get('Parameters')) > 0:
                for param in param_details.get('Parameters'):
                    param_path_array = param.get('Name').split("/")
                    config_name_position = len(param_path_array) - 1
                    config_name = param_path_array[config_name_position]
                    config_value = param.get('Value')
                    config_dict = {config_name: config_value}

                    if param.get('Type') != 'SecureString':
                        fields = config_dict
                        logger.debug(
                            f"ssm load found configuration {config_name}",
                            extra=fields)
                    else:
                        logger.debug(
                            f"ssm load found secure configuration {config_name}"
                        )

                    configuration.update(config_dict)
        except Exception as e:
            fields = {"ssm_parameter_path": ssm_parameter_path}
            logger.exception("Encountered an error loading config from SSM",
                             extra=fields)
            raise

        self.config = configuration
        return configuration
