class NormalizacionService:

    @staticmethod
    def normalizar_texto(texto: str) -> str:

        if texto:
            return texto.strip().title()
        return texto

    @staticmethod
    def normalizar_codigo(codigo: str) -> str:

        if codigo:
            return codigo.strip()
        return codigo