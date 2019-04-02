# Client Program System

## *Overview*

[TOC]



## Structure

```
    main-thread
          ||                          组件(Component)
  |\      \/                 |       |          crawllib, 'sites'
  | \   any thing            |  sys  |  subject
  |  |  need to do _______   | queue |  seleniumage # other-thread, daemon
  |  | 健  |      /        \ |       |            object
  |~~| 康  |     |   sys    || (prog |   taskage   # other-thread, daemon
  |~~| 度  |      \ manage / | tasks)|            online
  |~~|    \/       \-----/   └-------┘   --
  └--┘   Restart
         Program(Sytem)             systasks



```







## 附

### 鼓励自己的成就

#### 行数（工作量）

`new_main.py` -- ~100

`progtask.py` -- ~50

client/  # task->subject

  ├--`task.py` -- ~100

  └--`work.py` -- ~100

`online.py` -- ~50

crawllib/

  ├-- `__ini__.py` -- ~100

  └-- `resourcemange.py` -- ~300

observers/

  └-- `__init__.py` + `proxy.py` -- ~100

`sites/userindex.py` -- ~100