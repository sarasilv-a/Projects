using System.Security.Claims;
using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.AspNetCore.Components.Server.ProtectedBrowserStorage;
using MontagemBelasPizzas.Data.Entities.Utilizadores;

namespace MontagemBelasPizzas.UI.Authentication;

public class CustomAuthenticationStateProvider : AuthenticationStateProvider
{
    private readonly ProtectedLocalStorage _localStorage;
    private const string UserKey = "authenticatedUser";
    private Utilizador? _currentUser;

    public CustomAuthenticationStateProvider(ProtectedLocalStorage localStorage)
    {
        _localStorage = localStorage;
    }

    public override async Task<AuthenticationState> GetAuthenticationStateAsync()
    {
        // Durante a prerenderização, retorna um utilizador anónimo
        if (_currentUser is null)
        {
            var result = await _localStorage.GetAsync<Utilizador>(UserKey);
            if (result.Success && result.Value is not null)
            {
                _currentUser = result.Value;
            }
        }

        if (_currentUser is null)
        {
            var anonymous = new ClaimsPrincipal(new ClaimsIdentity());
            return new AuthenticationState(anonymous);
        }

        var claims = new List<Claim>
    {
        new(ClaimTypes.Name, _currentUser.Nome),
        new(ClaimTypes.Role, _currentUser.Tipo.ToString()),
        new(ClaimTypes.NameIdentifier, _currentUser.Id.ToString())
    };

        var identity = new ClaimsIdentity(claims, "CustomAuth");
        var user = new ClaimsPrincipal(identity);

        return new AuthenticationState(user);
    }


    public async Task Login(Utilizador user)
    {
        _currentUser = user;
        await _localStorage.SetAsync(UserKey, user);
        NotifyAuthenticationStateChanged(GetAuthenticationStateAsync());
    }

    public async Task Logout()
    {
        _currentUser = null;
        await _localStorage.DeleteAsync(UserKey);
        NotifyAuthenticationStateChanged(GetAuthenticationStateAsync());
    }
}
