program NegarBooleano;
var
    valor: boolean;
begin
    valor := true;

    writeln('Valor original: ', valor);

    valor := not valor;

    writeln('Valor negado: ', valor);
end.
