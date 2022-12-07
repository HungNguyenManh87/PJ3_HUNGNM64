export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-jpudacity.jp', // the auth0 domain prefix
    audience: 'Pj3', // the audience set for the auth0 app
    clientId: 'bVHHAQFGCGo55WRp5yUCH0syaYXLpFHu', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
