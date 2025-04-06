# Tema 1 ASC - Stan Andrei Razvan - 333CA

### Intro
[git repo](https://github.com/fynnceapa/le-stats-sportif)

Am avut de implementat o aplicatie client-server care sa gestioneze multiple request-uri.
Acest lucru trebuie facut intr-o maniera multi-threaded.

Timp de implementare ~ **6 ore**.

### Fisiere
```__init__.py``` - fisierul init.

```task_runner.py``` - contine impletarea pentru ThreadPool.

```routes.py``` - acest fisier contine rutele pentru Flask.

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

---

Clasa **TaskRunner** este clasa care proceseaza job-ul, practic este clasa pentru thread-uri.

Metoda **start_job** ia un job din queue, apeleaza metoda do_job si salveaza rezultatul pe disc.

---

**Sincronizarea** este asigurata de catre job_id-uri. Job_counter este o variabila care indica ce job se proceseaza. Aceasta este incrementata de fiecare data cand se adauga un job in queue (lucru tratat in routes.py). Prima data am crezut ca va trebui sa incrementez acest counter intr-o zona critica, dar dupa am realizat ca, datorita faptului ca eu adaug task-urile in routes, acest lucru nu va fi multi-threaded.

Totusi, pentru a fi sigur ca thread-urile vor lucra sincronizat, in momentul in care un thread scoate un job din queue, acest lucru este facut intr-o zona critica folosind un lock initializat in ThreadPool si pasat catre toate thread-urile.

### Routes

In routes se intampla mare parte din functionalitatea temei. Functia **add_job** este cea care se ocupa de adaugarea job-urilor in queue-ul threadpool-ului.

Conform cerintei, dupa ce se da shutdown nu mai pot fi adaugate job-uri (adica rutele POST) dar putem folosi rutele de GET pentru a vedea rezultatul unui job, numarul de job-uri etc.

Pe langa rutele care erau deja in schelet am mai adaugat si /api/graceful_shutdown, /api/num_jobs, /api/jobs.

### Logging

Am "log-uit" tot ce se intampla in routes, practic sunt logate toate cererile primite de la client catre server.

Am adaugat log-uri si in cazul unor erori. Fiind prima data cand am facut asta nu am stiut cat de detaliate sa le fac.
