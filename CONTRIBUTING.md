Contribuer
==========

Tout d'abord, merci de porter de l'intérêt à ce projet ! Vous trouverez dans ce document les bases de "comment contribuer" à ce projet.

## Communication

Ne soyez pas timide, demandez de l'aide ! Si vous avez une question, un commentaire, une préoccupation ou
une idée géniale, c'est l'occasion d'ouvrir un sujet pour lancer la conversation.

## Commits

* __Rebase__: Chaque fois que vous avez fait des commits sur votre copie locale en même temps que d'autres sur le upstream vous devez `rebase` au lieu de pull/merge. Rebasing fera passer les upstream commits avant vos commits locaux.
  
  ```sh
  git pull --rebase upstream
  ```

* __References__: Lorsque vous abordez une question, vous devez faire un `reference`
  à l'`issue` dans vos commits ou pull requests. Par exemple, si vous
  a abordé l'issue #42  la première ligne de votre message de commit doit être préfixée par
   `(gh-42)`.

## Tests

Tout code réalisé *devrait* passer par une suite de tests, car tout ce qui n'est pas testé est cassé. 

### Dépendances

Ce packet n'installe pad de dépendances de test.
Libre à vous d'installer `Nose` et `Mock`.
Ces dépendances peuvent être installées avec pip. 

```sh
pip install Nose Mock
```

### Lancer les Tests

Les tests peuvent être effectués aussi bien localement que par TravisCI. 

```sh
nosetests
```

## License

Ce projet est sous licence MIT.
