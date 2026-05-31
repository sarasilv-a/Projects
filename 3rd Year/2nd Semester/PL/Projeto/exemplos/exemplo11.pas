program ContarVogais;
var
    texto: string;
    i, contador: integer;
begin
    writeln('Introduza uma frase:');
    readln(texto);

    contador := 0;
    for i := 1 to length(texto) do
    begin
        if (texto[i] = 'a') or (texto[i] = 'e') or (texto[i] = 'i') or 
           (texto[i] = 'o') or (texto[i] = 'u') then
            contador := contador + 1;
    end;

    writeln('Número de vogais: ', contador);
end.
