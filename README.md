# Tema 1 ASC - Stan Andrei Razvan - 333CA

### Intro
Am avut de implementat o aplicatie client-server care sa gestioneze multiple request-uri.
  Acest lucru trebuie facut intr-o maniera multi-threaded.

### Fisiere
```__init__.py``` - fisierul init.

```task_runner.py``` - contine impletarea pentru ThreadPool.

```app/routes.py``` - acest fisier contine rutele pentru Flask.

```job.py``` - clasele pentru diferitele tipuri de job-uri.

```data_ingestor.py```  - aici se incarca fisierul csv.

### Clasele de job-uri

Am implementat diferitele job-uri prin clase polimorfice. Clasa **Job** este clasa de baza care este extinsa de restul.

Practic singura diferenta intre job-uri este metoda **do_job**, aceasta fiind implementata diferit in functie de caz.

Am ales aceasta abordare pentru implementarea diferitelor tipuri de job-uri pentru ca mi-a usurat munca in task_runner, tot ce ramane de facut aici pentru a completa un request este sa fie apelata metoda **do_job**.

### ThreadPool

ThreadPool-ul este implementat in fisierul task_runner.py.

L-am implementat folosind un queue si un numar de **TP_NUM_OF_THREADS** de thread-uri.

In ThreadPool am scris doua metode, cea de start care porneste thread-urile si o metoda de shutdown, unde se da join thread-urilor in cazul in care event-ul de shutdown este setat.

In ThreadPool se salveaza si statusurile job-urilor.

----

Clasa **TaskRunner** este clasa care proceseaza job-ul, practic este clasa pentru thread-uri. 
