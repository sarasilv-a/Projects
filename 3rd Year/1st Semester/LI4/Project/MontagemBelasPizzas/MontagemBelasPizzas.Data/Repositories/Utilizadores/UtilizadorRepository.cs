using MontagemBelasPizzas.Data.Interfaces;
using System.Collections.Generic;
using System.Threading.Tasks;
using MontagemBelasPizzas.Data.Entities.Utilizadores;

namespace MontagemBelasPizzas.Data.Repositories.Utilizadores
{
    public class UtilizadorRepository
    {
        private readonly ISqlDataAccess _db;

        public UtilizadorRepository(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<Utilizador?> GetById(int id)
        {
            var parameters = new { Id = id };
            var result = await _db.LoadData<Utilizador, dynamic>(
                storedProcedure: "spUtilizador_GetById",
                parameters: parameters
            );

            return result.FirstOrDefault();
        }

        public async Task<IEnumerable<Utilizador>> GetAll()
        {
            var result = await _db.LoadData<Utilizador, dynamic>(
                storedProcedure: "spUtilizador_GetAll",
                parameters: new { }
            );

            return result;
        }

        public async Task Insert(Utilizador utilizador)
        {
            utilizador.Senha = BCrypt.Net.BCrypt.HashPassword(utilizador.Senha);
            Console.WriteLine(utilizador.Senha);
            var parameters = new
            {
                utilizador.Nome,
                utilizador.Senha,
                utilizador.NIF,
                utilizador.DataDeNascimento,
                utilizador.ImagemURL,
                Tipo = utilizador.Tipo.ToString()
            };

            await _db.SaveData(
                storedProcedure: "spUtilizador_Insert",
                parameters: parameters
            );
        }

        public async Task Update(Utilizador utilizador)
        {
            utilizador.Senha = BCrypt.Net.BCrypt.HashPassword(utilizador.Senha);
            var parameters = new
            {
                utilizador.Id,
                utilizador.Nome,
                utilizador.Senha,
                utilizador.NIF,
                utilizador.DataDeNascimento,
                utilizador.ImagemURL,
                utilizador.QuantidadeDeProdutosRealizados,
                utilizador.QuantidadeDeProdutosRejeitados,
                utilizador.MediaDeSatisfacao,
                utilizador.TempoMedioPorProduto,
                utilizador.Tipo
            };

            await _db.SaveData(
                storedProcedure: "spUtilizador_Update",
                parameters: parameters
            );
        }

        public async Task Delete(int id)
        {
            var parameters = new { Id = id };

            await _db.SaveData(
                storedProcedure: "spUtilizador_Delete",
                parameters: parameters
            );
        }
        public async Task IncrementarPizzasRejeitadas(int id)
        {
            var parameters = new { Id = id };

            await _db.SaveData(
                storedProcedure: "spUtilizador_IncrementarPizzasRejeitadas",
                parameters: parameters
            );
        }

    }
}
