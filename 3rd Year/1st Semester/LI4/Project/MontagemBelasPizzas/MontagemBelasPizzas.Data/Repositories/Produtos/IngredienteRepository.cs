using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class IngredienteRepository
    {
        private readonly ISqlDataAccess _db;

        public IngredienteRepository(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<Ingrediente?> GetById(int id)
        {
            var parameters = new { Id = id };
            var result = await _db.LoadData<Ingrediente, dynamic>(
                storedProcedure: "spIngrediente_GetById",
                parameters: parameters
            );

            return result.FirstOrDefault();
        }

        public async Task<IEnumerable<Ingrediente>> GetAll()
        {
            var result = await _db.LoadData<Ingrediente, dynamic>(
                storedProcedure: "spIngrediente_GetAll",
                parameters: new { }
            );

            return result;
        }

        public async Task Insert(Ingrediente ingrediente)
        {
            var parameters = new
            {
                ingrediente.Nome,
                ingrediente.Preco,
                ingrediente.QuantidadeEmStock,
                ingrediente.EmUso,
                ingrediente.ImagemURL,
                ingrediente.IdAdministrador
            };

            await _db.SaveData("spIngrediente_Insert", parameters);
        }

        public async Task Update(Ingrediente ingrediente)
        {
            var parameters = new
            {
                ingrediente.Id,
                ingrediente.Nome,
                ingrediente.Preco,
                ingrediente.QuantidadeEmStock,
                ingrediente.EmUso,
                ingrediente.ImagemURL,
                ingrediente.IdAdministrador
            };

            await _db.SaveData("spIngrediente_Update", parameters);
        }

        public async Task Delete(int id)
        {
            var parameters = new { Id = id };
            await _db.SaveData("spIngrediente_Delete", parameters);
        }
    }
}
