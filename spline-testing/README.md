---

# Testing Spline

## Docker-based testing:
Based on `docker-compose` using internally Jmeter, one can run:

```bash
./run_jmetered_spline.py
```

Tests are defined in `./tests` directory, results are appended to the results (created if empty) in `./results` directory next to it.

There are certain requirements that must be met for the script to be used. Python-modules-wise, the requirements can be installed from the attached `requirements.txt` file using
```bash
pip install -r requirements.txt
```
As for environment requirements, following tools must be available on path:
    - `docker`
    - `docker-compose`
    - `git`
    - `mvn`

---

    Copyright 2019 ABSA Group Limited
    
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
        http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

