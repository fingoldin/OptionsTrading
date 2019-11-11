import setuptools

setuptools.setup(
  name="stocks",
  version="0.1",
  author="Vassilios Kaxiras,Rajat Mittal",
  author_email="vassilioskaxiras@gmail.com",
  description="Stock data scraper front-end",
  packages=setuptools.find_packages(),
  install_requires = ["mysqlclient"]
)
