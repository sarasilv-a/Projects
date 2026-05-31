using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class LinhaDeMontagemService
    {
        private readonly LinhaDeMontagemRepository _linhaDeMontagemRepository;

        public LinhaDeMontagemService(LinhaDeMontagemRepository linhaDeMontagemRepository)
        {
            _linhaDeMontagemRepository = linhaDeMontagemRepository;
        }

        public async Task<IEnumerable<LinhaDeMontagem>> GetLinhasDeMontagemByFuncionarioId(int funcionarioId)
        {
            return await _linhaDeMontagemRepository.GetByFuncionarioId(funcionarioId);
        }

        public async Task CreateLinhaDeMontagem(LinhaDeMontagem linha)
        {
            await _linhaDeMontagemRepository.Insert(linha);
        }
    }
}
