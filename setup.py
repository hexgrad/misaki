from setuptools import setup, find_packages

setup(
    name='misaki',
    version='0.6.5',
    packages=find_packages(),
    package_data={
        'misaki': ['data/*.json', 'data/*.txt', 'hangul/data/*.csv', 'hangul/data/*.tsv'],
    },
    install_requires=[
        'regex',
    ],
    extras_require={
        'en': ['num2words', 'spacy', 'spacy-curated-transformers', 'phonemizer'],
        'ja': ['fugashi', 'jaconv', 'mojimoji', 'unidic-lite'],
        'ko': ['g2pk2'],
        'zh': ['jieba', 'ordered-set', 'pypinyin', 'cn2an'],
        'vi': ['num2words', 'spacy', 'spacy-curated-transformers', 'underthesea'],
    },
    python_requires='>=3.7',
    author='hexgrad',
    author_email='hello@hexgrad.com',
    description='G2P engine for TTS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hexgrad/misaki',
    license='Apache 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
