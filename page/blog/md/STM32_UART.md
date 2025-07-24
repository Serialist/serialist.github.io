# STM32_UART

有五种接受方式：阻塞、中断、dma+中断、空闲+中断、dma+空闲+中断

有三种发送方式：阻塞、中断、dma+中断

## 接受

阻塞式

- HAL_UART_Transmit(&huart1, TxData, 5, 1000);

- HAL_UART_Receive(&huart1, RxData, 5, 1000);

中断式（使能中断）

- void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){}

- HAL_UART_Transmit_IT(&huart1, TxData, 5);

- HAL_UART_Receive_IT(&huart1, RxData, 5);

空闲中断（使能中断）

- void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size){}

- HAL_UART_Transmit_IT(&huart1, TxData, 5);

- HAL_UARTEx_ReceiveToIdle_IT(&huart1, RxData, 5);

DMA中断（配置DMA且使能中断）

- void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){}

- HAL_UART_Transmit_DMA(&huart1, TxData, 5);

- HAL_UART_Receive_DMA(&huart1, RxData, 5);

DMA空闲中断（配置DMA且使能中断）

- void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size){}

- HAL_UART_Transmit_DMA(&huart1, TxData, 5);

- HAL_UARTEx_ReceiveToIdle_DMA(&huart1, RxData, 5);