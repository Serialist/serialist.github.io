# STM32 串口

串口（串行接口 serial），指在一条线上一串一串的发送数据。相对的是并行接口，指在多条线上同时发送一排数据。

串口通过接收发送模式不同，分为：

1. 全双工

   可以同时发送和接受

2. 半双工

   可以发送或接受，但同时只能干一个

3. 单工

   只能接受或发送。接受者 = 不发送；发送者 = 不接受

在 STM32 上，提供了多种接受方式

五种接受方式：

1. 阻塞
2. 中断
3. DMA + 中断
4. 空闲中断
5. DMA + 空闲中断

三种发送方式：

1. 阻塞
2. 中断
3. DMA + 中断

# 怎么用

以 HAL 库为例，

## 接受

### 阻塞

- HAL_UART_Receive(&huart, data, size, timeout)

  

### 中断

- void HAL_UART_RxCpltCallback(&huart)

  中断回调函数，在这里 user 可以写接受的数据处理

- HAL_UART_Receive_IT(&huart, data, size)

### 空闲中断

- void HAL_UARTEx_RxEventCallback(&huart, size)
- HAL_UARTEx_ReceiveToIdle_IT(&huart, data, size)

### DMA中断

- void HAL_UART_RxCpltCallback(&huart)

- HAL_UART_Receive_DMA(&huart, data, size)

### DMA空闲中断

- void HAL_UARTEx_RxEventCallback(&huart, Size)

- HAL_UARTEx_ReceiveToIdle_DMA(&huart, data, size)

## 发送

### 阻塞

- HAL_UART_Transmit(&huart, data, size, 1000)


### 中断

- HAL_UART_Transmit_IT(&huart, data, size)


### 空闲中断

- HAL_UART_Transmit_IT(&huart, data, size)

### DMA中断

- HAL_UART_Transmit_DMA(&huart, data, size)