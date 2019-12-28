import click
import configparser
import sys
from pathlib import Path


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def load_config(cfg):
    if not Path(cfg).is_file():
        print("{} file does not exist or missing.".format(cfg))
        sys.exit(0)

    config = configparser.ConfigParser()
    config.read(cfg)
    return config


def parse_config_region(cfg, profile):
    config = load_config(cfg)

    if profile == "default":
        profile_key = profile
    else:
        profile_key = "profile {}".format(profile)

    region = config[profile_key].get('region')

    if not region:
        region = 'us-east-1'  # default to us-east-1 if no region set or found

    return region


def parse_credentials(cfg, profile):
    config = load_config(cfg)

    return {"key": config[profile]['aws_access_key_id'], "secret": config[profile]['aws_secret_access_key']}


def write_envrc(args_region, args_profile):
    home = str(Path.home())

    creds_file = '{}/.aws/credentials'.format(home)
    config_file = '{}/.aws/config'.format(home)

    profile = args_profile

    if args_region:
        region = args_region
    else:
        region = parse_config_region(config_file, profile)

    print('Generating .envrc for {} - {}'.format(profile, region))
    creds = parse_credentials(creds_file, profile)

    file = open('.envrc', 'w')
    file.write('export AWS_DEFAULT_REGION={}\n'.format(region))
    file.write('export AWS_ACCESS_KEY_ID={}\n'.format(creds.get("key")))
    file.write('export AWS_SECRET_ACCESS_KEY={}\n'.format(creds.get("secret")))
    file.close()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0')
def cli():
    pass


@click.command()
@click.option('--region', '-r', help='Specific region to set (e.g. us-west-2', required=False)
@click.option('--profile', '-p', default='default', help='name of the aws profile to generate env vars for', required=False)
def main(region, profile):
    """Generates .envrc based on your AWS config and credentials"""
    write_envrc(region, profile)