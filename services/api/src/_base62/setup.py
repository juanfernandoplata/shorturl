from setuptools import setup, Extension

module = Extension( "base62", sources = [ "base62.c" ] )

setup(
    name = "base62",
    version = "1.0",
    description = "A Python module for encoding and decoding integer values to/from base62",
    ext_modules = [ module ],
)
