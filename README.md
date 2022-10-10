# Auto schaduler

# Auto Run
If AWS or a private server runs source code without a tiny terminal, this approach helps.

## Plan
```mermaid
graph TD;
A(Clean_code) --> B[get_work_list]
B --> C{new_work?} --> D[work]
C --> G[get_new_work] --> B
D --> P{period} --> D
D --> E[report] --> F(End)
```

## Clean code
- python package tarfile with file filtering

## Test report
- EDA report
  - csv table
  
```
How to create report with python
```