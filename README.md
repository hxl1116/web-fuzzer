# Web Fuzzer
Web application fuzz testing tool

# Usage
  To run the CLI:
  `fuzz [discover | test] url OPTIONS`

  To run the docker image:
  `docker run --rm -it -p 80:80 andymeneely/swen331fuzzer`

### Commands:
  `discover`:
  Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
  
  `test`:
  Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.

### Options:
Options can be given in any order.

  `--custom-auth=string`:
  Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).

#### Discover options:
  `--common-words=file`:
  Newline-delimited file of common words to be used in page guessing. Required.
  
  `--extensions=file`:
  Newline-delimited file of path extensions, e.g. ".php". Optional. Defaults to ".php" and the empty string if not specified

#### Test options:
  `--common-words=file`:
  Same option as in discover - see above.
  
  `--extensions=file`:
  Same option as in discover - see above.
  
  `--vectors=file`:
  Newline-delimited file of common exploits to vulnerabilities. Required.
  
  `--sanitized-chars=file`:
  Newline-delimited file of characters that should be sanitized from inputs. Defaults to just < and >
  
  `--sensitive=file`:
  Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. Required.
  
  `--slow=500`:
  Number of milliseconds considered when a response is considered "slow". Optional. Default is 500 milliseconds

### Examples:
  `fuzz discover http://localhost:8080 --common-words=mywords.txt`:
  Discover inputs, default extensions, no login

  `fuzz discover http://localhost:8080 --custom-auth=dvwa --extensions=extensions.txt --common-words=mywords.txt`:
  Discover inputs to DVWA using our hard-coded authentication, port 8080

  `fuzz test http://localhost:8000 --custom-auth=dvwa --common-words=words.txt --vectors=vectors.txt --sensitive=creditcards.txt`:
  Discover and Test DVWA, port 8000, default extensions: sanitized characters, extensions and slow threshold