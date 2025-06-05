# GetPositionController

This document describes the `GetPositionController` in the CLI layer.

## Location

`src/app/cli_pfcf/controllers/get_position_controller.py`

## Responsibility

- Prompts the user for account ID and product code.
- Constructs a `GetPositionInputDto`.
- Invokes `GetPositionUseCase`.
- Displays the formatted output.

## Usage

1. Ensure the user is logged in.
2. Select the menu option for “Show Positions.”
3. Follow CLI prompts:
   - Enter account ID.
   - Enter product code (leave blank for all).
4. View the printed positions.

### Example

```bash
Enter your account: ABC12345
Enter product id (blank for all):
[
  {
    "investor_account": "ABC12345",
    "product_id": "TXFD4",
    ...
  },
  ...
]
```

## Design Notes

- Follows Clean Architecture: the controller coordinates input, use case, and output.
- Adheres to Single Responsibility Principle: only handles CLI interaction.
- Uses Dependency Inversion: depends on abstractions (`GetPositionUseCase`, `PositionRepositoryInterface`).
