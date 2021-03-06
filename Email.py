import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import date
from Investir import Log

class EnviaEmail:
    def __init__(self,sender_email,receiver_email,password, conteudo):
        self.port = 465  # For SSL
        self.password = password
        # Create a secure SSL context
        self.context = ssl.create_default_context()

        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.conteudo = self._formata_conteudo(conteudo)

        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = "Relatorio de Investimentos"
        self.message["From"] = self.sender_email
        self.message["To"] = self.receiver_email

        # Create the body of the message (a plain-text and an HTML version).
        self.html = f"""\
        <html>
          <head></head>
          <body>
            <p>  
                <h1 style="color: #5e9ca0;"> Alerta de email </h1>
                <br>Olá meu Caro,</br>
                <br>segue seu relatorio de investimentos de {date.today().strftime('%d/%m/%Y')}</br>
                <br><br>{self.conteudo}</br>
            </p>
          </body>
        </html>
        """
        self.part1 = MIMEText(self.html, 'html')
        self.message.attach(self.part1)

    def _formata_conteudo(self,conteudo):
        return str(conteudo).replace('\n','<br>').replace('\t','&emsp;')

    def insere_imagem(self, lista_imagens):
        Log.informacao('chamando metodo EnviaEmail.insere_imagem()')
        for x in lista_imagens:
            with open(x, 'rb') as f:
                content = MIMEImage(f.read(), _subtype='png')
                Log.informacao(f'imagem {x}, lida com sucesso')
                self.message.attach(content)

    def envia(self):
        Log.informacao('chamando metodo EnviaEmail.envia()')
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(
                self.sender_email, self.receiver_email, self.message.as_string()
            )
            Log.informacao(f'email enviado para {self.receiver_email}')
