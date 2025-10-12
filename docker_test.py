import docker


if __name__ == "__main__":
    print("Hello world")
    client = docker.from_env()