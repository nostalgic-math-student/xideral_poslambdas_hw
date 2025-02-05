# xideral_poslambdas_hw

- Josue Rojas Noble
## Tarea Sync POS <-> Infraestructura AWS

### Idea
Para esta tarea utilicé dos enfoques compatibles entre si: 

para la lambda function **syncPOSdata** la estrategia es simple: al ejecutarse se hace un barrido del s3 deseado para extraer la información de cada archivo y resumirlo en un archivo summary.csv dado.
La activación está ejecutada mediante **EventBridge** cada hora, suponiendo que los datos del POS se generan cada 2 horas para permitir que el s3 contenga siempre la información más reciente.

Para la lambda function **processPOSdata** la estrategia cambia: se ejecuta al reaccionar a un file upload del s3 deseado, y añade la ficha de información del archivo nuevo en el archivo summary.csv dado. 
Esta activación está monitoreada mediante el trigger **S3 create event**, por lo que a la hora de subir un archivo el s3 final (xideralcinedata-processed) se actualiza correctamente.

Se pueden mantener en activo ambas lambdas y no hay problema, este diseño permite tener a **processPOSdata** como principal método de manejo de datos, y relegar a **syncPOSdata** a un rol de seguro para siempre tener la información más reciente actualizada.

Nota: los archivos en Lambda tienen el nombre estándar lambda_function.py, fue cambiado al subirlo para identificarlos entre sí.
