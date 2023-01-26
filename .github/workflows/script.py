name: build
'on':
  push:
    branches:
    - master
  pull_request:
    branches:
    - master
env:
  DISPLAY: :99
  SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
jobs:
  build:
    strategy:
      matrix:
        os: windows-latest
        java:
        - 11
    runs-on: ${{ matrix.os }}
    steps:
    - name: Checkout GitHub repo
      uses: actions/checkout@v2
    - name: Set up Java
      uses: actions/setup-java@v2
      with:
        distribution: temurin
        java-version: ${{ matrix.java }}
    - name: Start Xvfb
      if: matrix.os == 'ubuntu-latest'
      run: Xvfb $DISPLAY &
    - name: Run tests on Linux
      if: matrix.os == 'ubuntu-latest'
      uses: nick-invision/retry@v2.7.1
      with:
        timeout_minutes: 30
        max_attempts: 3
        command: mvn -B test -Dtest=!Record*
    - name: Run tests on Mac
      if: matrix.os == 'macos-latest'
      uses: nick-invision/retry@v2.7.1
      with:
        timeout_minutes: 30
        max_attempts: 3
        command: mvn -B test -Dtest=!Docker*,!Record*
    - name: Run tests on Windows
      if: matrix.os == 'windows-latest'
      uses: nick-invision/retry@v2.7.1
      with:
        timeout_minutes: 30
        max_attempts: 3
        command: mvn -B test -Dtest=!Docker*
    - name: Upload analysis to SonarCloud
      if: success() && matrix.os == 'ubuntu-latest' && matrix.java == '11' && !contains(github.ref,
        'pull')
      run: 'mvn -B sonar:sonar -Dsonar.host.url=https://sonarcloud.io -Dsonar.organization=bonigarcia-github
        -Dsonar.projectKey=io.github.bonigarcia:webdrivermanager

        '
    - name: Upload coverage to Codecov
      if: success() && matrix.os == 'ubuntu-latest' && matrix.java == '11' && !contains(github.ref,
        'pull')
      uses: codecov/codecov-action@v1
    - name: Store recordings (only available in Windows)
      if: always() && matrix.os == 'windows-latest'
      uses: actions/upload-artifact@v3
      with:
        name: webm-files
        path: C:\Users\runneradmin\Downloads\*.webm
