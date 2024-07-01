FROM --platform=linux/amd64 golang:1.22 AS build-stage

WORKDIR /

COPY go.mod .
COPY main.go ./
COPY /server ./server

RUN CGO_ENABLED=0 GOOS=linux go build -o /app

FROM --platform=linux/amd64 gcr.io/distroless/base-debian11 AS final

WORKDIR /

COPY --from=build-stage /app /app

EXPOSE 8888

CMD [ "./app", "--type", "server" ]
