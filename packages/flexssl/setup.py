from distutils.core import setup, Extension

def main():
    setup(name="flexssl",
        version="1.0.0",
        description="Expands Python SSL Library with more methods",
        author="Anis Gandoura",
        author_email="agandoura@veepee.com",
        ext_modules=[
            Extension("flexssl", ["src/flexsslmodule.c"], libraries=["ssl"])
        ],)

if __name__ == "__main__":
    main()