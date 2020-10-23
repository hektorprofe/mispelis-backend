# Instrucciones

## Versiones disponibles en el repositorio

### Unidad 2: Autenticación

- **Unidad2.1**
- **Unidad2.2**: Versión final

```bash
# Recuperar una versión determinada
git checkout <version>

# Ejemplo
git checkout Unidad2.2
git checkout master
```

Instalar entorno virtual:

```bash
pip install pipenv

cd server
pipenv install -r requirements.txt

pipenv run server
```

Usuarios de prueba:

- **admin**: admin@admin.com:1234
- **test**: test@test.com:12345678
