from core.asgi import *
import pywhatkit

pywhatkit.sendwhatmsg_instantly(  # type: ignore
    '+543814755771', 'Whatsapp Bot: Prueba de notificacion de Vencimiento.', 15, True, 5)  # type: ignore
