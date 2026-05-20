# Google Batch tutorial

:::{warning} Προσοχή!
Η εκτέλεση των παρακάτω εντολών συνεπάγεται χρήση των υπηρεσιών υπολογιστικού νέφους της Google και θα επιφέρουν χρεώσεις.
Η εκτέλεση γίνεται με ευθύνη των χρηστών.
:::

## Εγκατάσταση Google Cloud CLI
Για την εκτέλεση των παρακάτω εντολών που ακολουθούν απαιτείται η εγκατάσταση του Google Cloud CLI.
Περισσότερες οδηγίες στο [https://docs.cloud.google.com/sdk/docs/install-sdk](https://docs.cloud.google.com/sdk/docs/install-sdk)

## Σύνδεση στο Google Cloud

```bash
gcloud auth login
```


## Δημιουργία νέου project

```bash
gcloud projects create gini-2026 --name="Gini"
```

## Ανάκτηση λίστας με τα υφιστάμενα projects

```bash
gcloud projects list
```
προσάρτηση του project ID σε μια μεταβλητή

```bash
PROJECT_ID=$(gcloud config get-value project)
```

##  ορισμός active project:

```bash
gcloud config set project $PROJECT_ID
```

## Επιβεβαίωση active project:

```bash
gcloud config get-value project
```

## Τιμολόγηση (Billing)

Για την χρήση των υπηρεσιών νέφους είναι απαραίτητη η σύνδεση ενός λογαριασμού χρέωσης με το project.

## Ανάκτηση λίστας με τα υφιστάμενα billing accounts

```bash
gcloud billing accounts list
```

σύνδεση του project με ένα billing account:

```bash
gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
```

## ενεργοποίηση των απαιτούμενων APIs

```bash
gcloud services enable artifactregistry.googleapis.com batch.googleapis.com
```



## Ορισμός μεταβλητών για γενικότερη χρήση

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
SA_EMAIL="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"
```

Δώσε στον λογαριασμό υπηρεσίας (serviceAccount) μου, με συγκεκριμένο email (SA_EMAIL), το δικαίωμα (roles/batch.agentReporter) να αναφέρει την πρόοδο των εργασιών Batch που εκτελεί μέσα στο έργο μου (PROJECT_ID).

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/batch.agentReporter"
```

Δίνει στον λογαριασμό υπηρεσίας (Service Account) πλήρη έλεγχο πάνω στα αρχεία του Google Cloud Storage (GCS).

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectAdmin"
```

## Δημιουργία Cloud Storage bucket
Η παρακάτω εντολή δημιουργεί έναν καινούργιο, ασφαλή χώρο αποθήκευσης (Bucket) στο Google Cloud Storage με το όνομα <YOUR_UNIQUE_BUCKET_NAME>.

(Το  <YOUR_UNIQUE_BUCKET_NAME> είναι ένας placeholder, ορίστε ένα όνομα όπως πχ my_bucket).

Παρακάτω αναλύεται η κάθε παράμετρος ξεχωριστά:

    - gcloud storage buckets create gs://YOUR_UNIQUE_BUCKET_NAME: Είναι η βασική εντολή που δημιουργεί το bucket. Το όνομα του θα είναι YOUR_UNIQUE_BUCKET_NAME και η διεύθυνσή του στο cloud ξεκινά πάντα με το gs://.

    - default-storage-class=STANDARD: Ορίζει την κλάση αποθήκευσης σε Standard. Είναι η ιδανική επιλογή για αρχεία στα οποία ο χρήστης έχει συχνή πρόσβαση (high-frequency access), καθώς δεν έχει χρέωση για την ανάκτηση των δεδομένων και προσφέρει τη μέγιστη ταχύτητα.

    - location=US-CENTRAL1: Ορίζει τη γεωγραφική τοποθεσία (Data Center) όπου θα αποθηκεύονται φυσικά τα αρχεία (στην κεντρική Αμερική).

    - uniform-bucket-level-access: Ενεργοποιεί την ομοιόμορφη πρόσβαση. Αυτό σημαίνει ότι τα δικαιώματα (ποιος βλέπει τι) ορίζονται συνολικά για όλο το bucket (μέσω IAM) και όχι ξεχωριστά για κάθε αρχείο (ACLs). Είναι η πιο σύγχρονη και ασφαλής πρακτική διαχείρισης.

    - public-access-prevention: Κλειδώνει το bucket ώστε να μην μπορεί ποτέ κανένα αρχείο να γίνει δημόσια προσβάσιμο στο internet κατά λάθος. Ακόμα κι αν κάποιος προσπαθήσει να δώσει πρόσβαση σε όλους, το Google Cloud θα το μπλοκάρει.


```bash
gcloud storage buckets create gs://YOUR_UNIQUE_BUCKET_NAME \
    --default-storage-class=STANDARD \
    --location=US-CENTRAL1 \
    --uniform-bucket-level-access \
    --public-access-prevention
```

## Ανέβασμα αρχείων

Η παρακάτω εντολή  ανεβάζει (κάνει copy) τοπικά αρχεία και φακέλους από τον τοπικό υπολογιστή μέσα στο Google Cloud Bucket (YOUR_UNIQUE_BUCKET_NAME) που δημιουργήθηκε πριν.

```bash
gcloud storage cp -r ./data gs://YOUR_UNIQUE_BUCKET_NAME/
gcloud storage cp -r ./tiffs gs://YOUR_UNIQUE_BUCKET_NAME/
gcloud storage cp year_fua_list.txt gs://YOUR_UNIQUE_BUCKET_NAME/
```

Επιβεβαίωση του περιεχομένου στο gs://YOUR_UNIQUE_BUCKET_NAME/

```bash
gcloud storage ls gs://YOUR_UNIQUE_BUCKET_NAME/
```

## Docker repository

### Δημιουργία του Artifact Registry repository

Η επόμενη εντολή δημιουργεί μια ιδιωτική αποθήκη (Repository) στο Artifact Registry του Google Cloud, με το όνομα gini-repo, ειδικά σχεδιασμένη για να αποθηκεύονται εκεί οι εικόνες Docker (Docker images) της εφαρμογής.

Πιο αναλυτικά:

    gcloud artifacts repositories create gini-repo: Είναι η βασική εντολή που ζητά τη δημιουργία ενός νέου repository στο Artifact Registry με το όνομα gini-repo.

    --repository-format=docker: Καθορίζει τον τύπο των αρχείων που θα φιλοξενεί. Δηλώνει στη Google ότι αυτό το repo θα δέχεται αποκλειστικά Docker images (και όχι πακέτα Python, Node.js, Java κ.λπ., τα οποία επίσης υποστηρίζει το Artifact Registry).

    --location=us-central1: Ορίζει ότι η αποθήκη θα δημιουργηθεί φυσικά στο data center της κεντρικής Αμερικής (us-central1). Είναι καλή πρακτική να βρίσκεται στην ίδια περιοχή με το Cloud Storage bucket που δημιούργησες πριν, για μεγαλύτερη ταχύτητα και χαμηλότερο κόστος μεταφοράς δεδομένων.

    --description="Docker repository for Gini calculation": Μια απλή περιγραφή (σχόλιο) για το ποιος είναι ο σκοπός αυτού του repository (εδώ: για τα Docker images που θα τρέχουν τους υπολογισμούς του δείκτη Gini).

```bash
gcloud artifacts repositories create gini-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Gini calculation"
```

Η παρακάτω εντολή συνδέει το τοπικό Docker με το Google Cloud, ώστε να μπορεί να ανεβάζει ο χρήστης (push) ή να κατεβάζει (pull) εικόνες (images) από το Container Registry της Google

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```


### Εικόνα Docker

Η εντολή στην συνέχεια δημιουργεί (κτίζει) μια εικόνα Docker (Docker image) από τον κώδικα και της δίνει ένα πολύ συγκεκριμένο όνομα (tag), ώστε να είναι έτοιμη για να ανέβει στο Artifact Registry του Google Cloud.

Το κάθε κομμάτι αναλυτικά:

    docker build: Είναι η βασική εντολή που λέει στο Docker να διαβάσει το αρχείο Dockerfile που είναι στον  τοπικό φάκελό και να δημιουργήσει το image.

    -t (Tag): Σημαίνει "δώσε αυτό το όνομα/ετικέτα στο image που θα φτιαχτεί".

    us-central1-docker.pkg.dev/$PROJECT_ID/gini-repo/processor:v1: Αυτό είναι το πλήρες όνομα (URL προορισμού) του image. Χωρίζεται ως εξής:

        us-central1-docker.pkg.dev: Η διεύθυνση του Artifact Registry της Google.

        /$PROJECT_ID/: Το αναγνωριστικό του project στο Google Cloud.

        /gini-repo/: Η αποθήκη (repository) που δημιούργησες πριν.

        /processor: Το όνομα που επιλέγεται σε αυτή τη συγκεκριμένη εφαρμογή.

        :v1: Η έκδοση (version) του κώδικα.

    . (η τελεία στο τέλος): Είναι εξαιρετικά σημαντική! Λέει στο Docker: "Ψάξε για το Dockerfile και τα αρχεία του κώδικα εδώ ακριβώς, στον τρέχοντα φάκελο που βρίσκομαι τώρα στο τερματικό".

```bash
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/gini-repo/processor:v1 .
```

Αυτή η εντολή ανεβάζει (κάνει upload) το Docker image που μόλις έγινε στον τοπικό υπολογιστή, μέσα στην ιδιωτική αποθήκη (Artifact Registry) στο Google Cloud.

```bash
docker push us-central1-docker.pkg.dev/$PROJECT_ID/gini-repo/processor:v1
```

Επιβεβαίωση με την παρακάτω η εντολή η οποία εμφανίζει μια λίστα με όλα τα Docker images που έχει ανεβάσει ο χρήστης στη συγκεκριμένη αποθήκη (gini-repo) στο Google Cloud, 
δείχνοντας ταυτόχρονα και τις εκδόσεις (tags) τους

```bash
gcloud artifacts docker images list us-central1-docker.pkg.dev/$PROJECT_ID/gini-repo --include-tags
```
## Απόδοση δικαιωμάτων
Αυτές οι δύο παρακάτω εντολές δίνουν απαραίτητα δικαιώματα ασφαλείας στον προεπιλεγμένο λογαριασμό υπηρεσίας (Compute Engine Service Account) του Project.

Απόδοση του δικαιώματος του Αναγνώστη (Reader) στο Artifact Registry και Batch Agent Reporter.

```bash

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/batch.agentReporter"
```

Προαιρετικά εντολές για την παραμετροποίηση του δικτύου (network configuration):

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-cloudbatch.iam.gserviceaccount.com" \
   --role="roles/compute.networkUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member="serviceAccount:service-$PROJECT_NUMBER@compute-system.iam.gserviceaccount.com" \
   --role="roles/compute.networkUser"
```

Στην συνέχεια ενεργοποιείται μια εξαιρετικά χρήσιμη λειτουργία ασφαλείας και δικτύωσης στο Google Cloud, που ονομάζεται Private Google Access (Ιδιωτική Πρόσβαση Google), για το προεπιλεγμένο υποδίκτυο (default) στην περιοχή της κεντρικής Αμερικής (us-central1).

Ας δούμε τι σημαίνει κάθε κομμάτι:

    gcloud compute networks subnets update default: Ζητάει να τροποποιηθεί (να γίνει update) ένα υπάρχον υποδίκτυο με το όνομα default.

    --region=us-central1: Καθορίζει ότι η αλλαγή θα γίνει στο υποδίκτυο που βρίσκεται στη συγκεκριμένη γεωγραφική περιοχή.

    --enable-private-ip-google-access: Ενεργοποιεί το Private Google Access.

```bash
gcloud compute networks subnets update default \
    --region=us-central1 \
    --enable-private-ip-google-access
```



## Υποβολή της εργασίας (Submit Batch job) στο υπολογιστικό νέφος

Αυτή η εντολή δίνει την εντολή εκκίνησης στη Google:

    submit $JOB_NAME: Καλεί την υπηρεσία Cloud Batch ώστε να ξεκινήσει μια νέα εργασία με το όνομα που ορίστηκε στη μεταβλητή JOB_NAME".

    --location us-central1: Ορίζει ότι το υπολογιστικό σύστημα του Cloud Batch που θα διαχειριστεί την εργασία (scheduling) θα βρίσκεται στην κεντρική Αμερική.

    --config job.json: Παρέχει στη Google ένα αρχείο ρυθμίσεων (job.json) το οποίο περιγράφει τι πρέπει να κάνει η εργασία.
Αυτό το αρχείο συνδέει όλα όσα δημιουργήθηκαν στα προηγούμενα βήματα. Ουσιαστικά καλεί την Google να κάνει τις παρακάτω διαδικασίες:

    - Ανάρτηση μιας εικονικής μηχανής (VM) στο δίκτυο με το Private Google Access.

    - Λήψη του  Docker image processor:v1 από το Artifact Registry.

    - ανάγνωση των δεδομένων από το Cloud Storage bucket gs://YOUR_UNIQUE_BUCKET_NAME.

    - εκτέλεση του Gini κώδικα και αποθήκευση των αποτελεσμάτων.


```bash
JOB_NAME="gini-job-$(date +%Y%m%d-%H%M)"
gcloud batch jobs submit $JOB_NAME --location us-central1 --config job.json
```

η εντολή στο επόμενο βήμα χρησιμοποιείται για την παρακολούθηση της πορεία της εργασίας, 
εμφανίζοντας το αναλυτικό ιστορικό των γεγονότων (events) και της κατάστασής της σε πραγματικό χρόνο.

```bash
gcloud batch jobs describe $JOB_NAME --location us-central1 --format='value(status.statusEvents)'
```

## Λήψη των αποτελεσμάτων
Τέλος, με την επόμενη εντολή λαμβάνονται τα τελικά αποτελέσματα του υπολογισμού από το Google Cloud Storage στον τοπικό υπολογιστή του χρήστη.

```bash
gcloud storage cp -r gs://YOUR_UNIQUE_BUCKET_NAME/output/ ~/Desktop/output_gini
```
## Απαραίτητα αρχεία
Στον παρακάτω σύνδεσμο θα ορισμένα χρήσιμα αρχεία που αφορούν την εκτέλεση του κώδικα:

- το [αρχείο Dockerfile στο GitHub](https://github.com/kokkytos/gee/blob/main/data/google_batch/Dockerfile).
- το [αρχείο gini.py στο GitHub](https://github.com/kokkytos/gee/blob/main/data/google_batch/gini.py).
- το [αρχείο job.json στο GitHub](https://github.com/kokkytos/gee/blob/main/data/google_batch/job.json).
- το [αρχείο process_list.py στο GitHub](https://github.com/kokkytos/gee/blob/main/data/google_batch/process_list.py).
- το [αρχείο year_fua_list.txt στο GitHub](https://github.com/kokkytos/gee/blob/main/data/google_batch/year_fua_list.txt).

Τα δεδομένα ωστόσο δεν διανέμονται.

## Σημαντικοί υπερσύνδεσμοι στο google cloud

- https://console.cloud.google.com/batch/
- https://console.cloud.google.com/artifacts
- https://console.cloud.google.com/storage/