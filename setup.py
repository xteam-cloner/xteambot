import re
import setuptools

def get_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("xteam/version.py", "rt", encoding="utf8") as x:
    version = re.search(r'__version__ = "(.*?)"', x.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xteam",
    version=version,
    author="TeamX",
    author_email="xteamji@gmail.com",
    description="A Secure and Powerful Python-Telethon Based Library For xteam Userbot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xteam-cloner/xteambot",
    project_urls={
        "Bug Tracker": "https://github.com/xteam-cloner/xteambot/issues",
        "Source Code": "https://github.com/xteam-cloner/xteambot",
    },
    license="GNU AFFERO GENERAL PUBLIC LICENSE (v3)",
    packages=setuptools.find_packages(),
    include_package_data=True, 
    package_data={
        "xteam": [
            "resources/*", 
            "plugins/*", 
            "strings/*", 
            "assistant/*"
        ],
    },
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "xteambot=xteam.__main__:main", 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8, <3.13",
)
