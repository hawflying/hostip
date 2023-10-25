import os
import configparser

# 默认配置，输入域名
DEFAULT_INPUT_DOMAINS = """github.com
github.io
github.blog
github.community
api.github.com
gist.github.com
live.github.com
alive.github.com
central.github.com
codeload.github.com
collector.github.com
education.github.com
assets-cdn.github.com
avatars.githubusercontent.com
avatars0.githubusercontent.com
avatars1.githubusercontent.com
avatars2.githubusercontent.com
avatars3.githubusercontent.com
avatars4.githubusercontent.com
avatars5.githubusercontent.com
raw.githubusercontent.com
camo.githubusercontent.com
cloud.githubusercontent.com
media.githubusercontent.com
desktop.githubusercontent.com
favicons.githubusercontent.com
objects.githubusercontent.com
user-images.githubusercontent.com
pipelines.actions.githubusercontent.com
github-com.s3.amazonaws.com
github-cloud.s3.amazonaws.com
github-production-user-asset-6210df.s3.amazonaws.com
github-production-release-asset-2e65be.s3.amazonaws.com
github-production-repository-file-5c1aeb.s3.amazonaws.com
githubstatus.com
github.githubassets.com
github.map.fastly.net
github.global.ssl.fastly.net
vscode.dev
api.funcaptcha.com"""
# 默认配置，支持的最大域名数量
MAX_DOMAIN_COUNT = 300

# 配置文件名称和部分名称
CONFIG_FILE = 'config.ini'
CONFIG_SECTION = 'General'

class Config:
    def __init__(self):
        self._default_input_domains, self._max_domain_count = self._read_config()

    @property
    def default_input_domains(self):
        return self._default_input_domains
    
    @property
    def max_domain_count(self):
        return self._max_domain_count

    def _read_config(self):
        config = configparser.ConfigParser()

        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE, encoding='utf-8')

        # 从配置文件中读取值
        default_input_domains = config.get(CONFIG_SECTION, 'default_input_domains', fallback=DEFAULT_INPUT_DOMAINS)
        max_domain_count = config.getint(CONFIG_SECTION, 'max_domain_count', fallback=MAX_DOMAIN_COUNT)

        return default_input_domains, max_domain_count