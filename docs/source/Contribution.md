# Contribute as a user

The documentation, examples and tutorials should be understandable and the code bug-free.
All users have different backgrounds, so you may not understand everything or encounter bugs.
In that case, PLEASE raise an issue [here](https://github.com/RWTH-EBC/AixWeather/issues/new/choose).

# Contribute as a developer

If you instead want to contribute new features or fix bugs yourself, we are more than happy.

Please also raise an issue and create a new branch labeled `issueNR-issueName`.

Once your feature is ready, create a pull request and check if the pipeline succeeds.
Assign a reviewer before merging. Once the review is finished, you can merge.

Please note that the main branch is used in the WebApp and therefore changes here must be in 
line with the current version of the WebApp. Updates to the main branch that affect 
functionalities require therefore a PYPI RELEASE. The VM that hosts the WebApp must be updated.
Pull requests should merge into the development first. The development branch contains a working 
version which can be functionally ahead of the WebApp.


**Before** implementing or modifying modules, classes or functions, please read the following page.

## Styleguide
We use PEP8 as a style guide. Some IDEs (like PyCharm) automatically show you code that is not in PEP8. If you don't have such an IDE, please read [this page](https://pep8.org/) to get a better understanding of it.

## Documentation
All created or modified functions should be documented properly. Try to follow the structure already present. If possible, write a little doctest example into the docstring to make clear to users what the desired output of your function is. All non-self-explanatory lines of code should include a comment. We use the pycharm-style for docstrings, e.g.
```python
def foo(dummy):
    """
    Describe what the function does in here.
    The blank line below is necessary for the doc to render nicely.

    Args:
        dummy (str): Any parameter description
    Returns:
        pd.Dataframe: Return description
    """
```

## Unit-Tests
Especially when creating new functions or classes, you have to add a unit-test function.
Open the `\tests`-directory. If you create a new module, you have to create a new 
`test_my_new_module.py` file and follow the existing structure of the 
other test-files.

If you are not familiar with unit-tests, here is a quick summary:
- Test as many things as possible. Even seemingly silly tests like correct input-format help prevent future problems for new users
- use the `self.assertSOMETHING` functions provided by `unittest`. This way, a test failure is presented correctly An error inside your test function will not be handeled as a failure but an error.
- If the success of your test depends on the used device, you can use decorators like `skip()`, `skipif(numpy.__version__<(1, 0), "not supported with your numpy version")`, etc. 
- `setUp()` and `tearDown()` are called before and after each test. Use this functions to define parameters used in every test, or to close applications like Dymola once a test is completed.
- See the [unittest-documentation](https://docs.python.org/3/library/unittest.html#organizing-tests) for further information

You can check your work by running all tests before commiting to git. 

## Pylint
With pylint we try to keep our code clean.  
See the description in [this repo](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/templates/tree/master/pylint) on information on what pylint is and how to use it.
