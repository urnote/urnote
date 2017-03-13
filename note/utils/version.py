def get_version(version):
    # build the two parts of the version number:
    # major = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    major = get_major_version(version)

    sub = ''
    if version[3] != 'final':
        mapping = {'pre-alpha': '.dev', 'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]]

    return major + sub


def get_major_version(version):
    """Returns major version from VERSION."""
    parts = 2 if version[2] == 0 else 3
    major = '.'.join(str(x) for x in version[:parts])
    return major
