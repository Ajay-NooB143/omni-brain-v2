from setuptools import setup, find_packages

setup(
    name="omni-brain-v2",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "anthropic>=0.25.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "master-bot=master_bot_runner:main",
            "worker-bot=worker_bot_runner:main",
        ],
    },
)