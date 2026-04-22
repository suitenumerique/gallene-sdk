import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

from api import GaleneAPI

def main():
    print("Hello from galene-api-wrapper!")
    api = GaleneAPI(url="https://dty-s26-p2-galene.k8s-cloud.centralesupelec.fr/")
    print(api.list_groups())


if __name__ == "__main__":
    main()
